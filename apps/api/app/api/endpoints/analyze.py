from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from supabase_client import supabase
from datetime import datetime
import uuid
import os
from pathlib import Path

from app.core.config import settings
from app.core.logger import get_logger
from app.core.dependencies import get_current_user, UserSchema, get_resume_parser, get_llm_service
from app.models.schemas import ParsedResume
from app.models.agent_schemas import (
    FinalApplicationPackage,
    ApplicationGenerationRequest,
    GeneratedMaterialsResponse,
    UpdateGeneratedMaterialsRequest,
)
from app.models.store import resume_store

from app.services.resume_parser import ResumeParserService
from app.services.matching_service import MatchingService
from app.services.cover_letter_service import CoverLetterService
from app.services.llm_service import LLMService
from app.agents.workflow import ApplicationWorkflow
from app.agents.resume_tailor_agent import ResumeTailorAgent
from app.agents.email_agent import EmailAgent
from app.utils.pdf_extractor import extract_text_from_pdf

logger = get_logger(__name__)
router = APIRouter()

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # MB → bytes

def get_matching_service(
    llm_svc=Depends(get_llm_service),
) -> MatchingService:
    return MatchingService(llm_svc)

def get_cover_letter_service(
    llm_svc=Depends(get_llm_service),
) -> CoverLetterService:
    return CoverLetterService(llm_svc)

def get_resume_tailor_agent(llm=Depends(get_llm_service)) -> ResumeTailorAgent:
    return ResumeTailorAgent(llm)

def get_email_agent(llm=Depends(get_llm_service)) -> EmailAgent:
    return EmailAgent(llm)

def get_application_workflow(
    llm=Depends(get_llm_service),
    matcher=Depends(get_matching_service),
    cover_letter_gen=Depends(get_cover_letter_service),
    tailor=Depends(get_resume_tailor_agent),
    email_ag=Depends(get_email_agent)
) -> ApplicationWorkflow:
    return ApplicationWorkflow(llm, matcher, cover_letter_gen, tailor, email_ag)


def _persist_application_record(payload: dict):
    try:
        return supabase.table("applications").insert(payload).execute()
    except Exception as db_err:
        if "email_subject" in payload:
            logger.warning(f"Retrying application insert without email_subject: {db_err}")
            fallback_payload = {k: v for k, v in payload.items() if k != "email_subject"}
            return supabase.table("applications").insert(fallback_payload).execute()
        raise


def _update_application_record(application_id: str, user_id: str, payload: dict):
    try:
        return (
            supabase.table("applications")
            .update(payload)
            .eq("id", application_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as db_err:
        if "email_subject" in payload:
            logger.warning(f"Retrying application update without email_subject: {db_err}")
            fallback_payload = {k: v for k, v in payload.items() if k != "email_subject"}
            return (
                supabase.table("applications")
                .update(fallback_payload)
                .eq("id", application_id)
                .eq("user_id", user_id)
                .execute()
            )
        raise


@router.post("/analyze", response_model=FinalApplicationPackage)
async def analyze_resume(
    file: UploadFile = File(..., description="PDF resume file"),
    preferred_field: str = Form(default="Software Engineering"),
    location: str = Form(default="Remote"),
    current_user: UserSchema = Depends(get_current_user),
    parser: ResumeParserService = Depends(get_resume_parser),
    workflow: ApplicationWorkflow = Depends(get_application_workflow)
):
    """
    Unified endpoint to parse a resume PDF and immediately run the multi-agent job discovery,
    matching, and cover letter generation pipeline.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB.")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    resume_id = str(uuid.uuid4())
    
    try:
        # Store PDF in Supabase Storage instead of local filesystem
        try:
            supabase.storage.from_("resumes").upload(f"{resume_id}.pdf", content)
            logger.info(f"Uploaded resume {resume_id}.pdf to Supabase storage")
        except Exception as storage_err:
            logger.warning(f"Failed to upload PDF to Supabase storage: {storage_err}")

        # Phase 1: Resume Parsing
        raw_text = extract_text_from_pdf(content)
        parsed: ParsedResume = parser.parse(raw_text)

        # Store Resume in Supabase
        try:
            supabase.table("resumes").insert({
               "user_id": current_user.id,
               "resume_text": raw_text,
               "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as db_err:
            logger.warning(f"Failed to store resume in DB: {db_err}")
        
        # Also store in memory store for other endpoints if they need it
        resume_store.save(resume_id, parsed)
        
        # Phase 2: Run discovery and matching ONLY
        package = workflow.run_discovery(
            resume_id=resume_id,
            parsed_resume=parsed,
            preferred_field=preferred_field,
            location=location
        )

        return package

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error during analysis: {str(e)}")

@router.post("/generate-application", response_model=GeneratedMaterialsResponse)
async def generate_application(
    request: ApplicationGenerationRequest,
    current_user: UserSchema = Depends(get_current_user),
    workflow: ApplicationWorkflow = Depends(get_application_workflow)
):
    """
    Stage 2: Takes a selected internship and runs Resume Tailoring, and Email Generation.
    """
    parsed_resume = resume_store.get(request.resume_id)
    if not parsed_resume:
        raise HTTPException(status_code=404, detail="Resume context expired. Please re-upload your resume on the dashboard.")
        
    try:
        materials = workflow.run_generation(
            resume_id=request.resume_id,
            parsed_resume=parsed_resume,
            internship=request.internship,
            user_name=current_user.name,
            user_email=current_user.email
        )
        
        # Store complete application in DB
        application_id = None
        try:
            insert_response = _persist_application_record({
                "user_id": current_user.id,
                "company": request.internship.company,
                "role": request.internship.role,
                "match_score": request.match_score,
                "reasoning": request.reasoning,
                "cover_letter": materials.cover_letter,
                "tailored_resume": materials.tailored_resume,
                "email_subject": materials.email_subject,
                "email_body": materials.email_body,
                "created_at": datetime.utcnow().isoformat()
            })
            if insert_response.data:
                application_id = insert_response.data[0].get("id")
        except Exception as db_err:
            logger.warning(f"Failed to store application record for {request.internship.company}: {db_err}")

        materials.application_id = application_id
        return materials
        
    except Exception as e:
        logger.error(f"Generation pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error during generation: {str(e)}")


@router.put("/application-materials")
async def update_generated_materials(
    request: UpdateGeneratedMaterialsRequest,
    current_user: UserSchema = Depends(get_current_user),
):
    payload = {
        "tailored_resume": request.tailored_resume,
        "cover_letter": request.cover_letter,
        "email_subject": request.email_subject,
        "email_body": request.email_body,
    }

    try:
        response = _update_application_record(request.application_id, current_user.id, payload)
        if not response.data:
            raise HTTPException(status_code=404, detail="Application record not found.")

        return {
            "status": "success",
            "application_id": request.application_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update generated materials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save edited materials: {str(e)}")
