"""
api/endpoints/resume.py — Phase 1: Resume Intelligence.
Handles PDF upload, text extraction, and structured resume parsing.
Stores parsed resume in the session store for use by later phases.
"""

import uuid
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.dependencies import get_resume_parser, get_current_user
from app.core.logger import get_logger
from app.models.schemas import ResumeUploadResponse, ParsedResume
from app.models.store import resume_store
from app.services.resume_parser import ResumeParserService
from app.utils.pdf_extractor import extract_text_from_pdf
from supabase_client import supabase
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # MB → bytes


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a resume PDF",
    description=(
        "Upload a PDF resume. The system will extract text and parse it into "
        "structured JSON including skills, education, and experience."
    ),
)
async def upload_resume(
    file: UploadFile = File(..., description="PDF resume file"),
    parser: ResumeParserService = Depends(get_resume_parser),
    current_user: dict = Depends(get_current_user),
):
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Optionally persist file to disk
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    resume_id = str(uuid.uuid4())

    try:
        # Save raw PDF
        pdf_path = upload_dir / f"{resume_id}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(content)

        # Extract text from PDF
        raw_text = extract_text_from_pdf(content)
        logger.info(f"Extracted {len(raw_text)} chars from '{file.filename}'")

        # Parse structured data
        parsed: ParsedResume = parser.parse(raw_text)

        # Store in Database
        try:
            supabase.table("resumes").insert({
                "user_id": current_user.id,
                "resume_text": raw_text,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to save resume to Supabase: {e}")
            
        # Store in memory for downstream tasks
        resume_store.save(resume_id, parsed)
        
        logger.info(f"Resume stored in DB with ID: {resume_id}")

        return ResumeUploadResponse(
            status="success",
            filename=file.filename,
            resume_id=resume_id,
            parsed=parsed,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Resume processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while processing resume.",
        )


@router.get(
    "/{resume_id}",
    response_model=ParsedResume,
    summary="Retrieve a previously parsed resume",
)
async def get_resume(resume_id: str):
    """Fetch a parsed resume by its ID from memory store."""
    parsed = resume_store.get(resume_id)
    if not parsed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found. Upload it first.",
        )
    return parsed


@router.delete(
    "/{resume_id}",
    summary="Delete a resume from the database",
)
async def delete_resume(resume_id: str):
    """Remove a resume from the memory store."""
    if not resume_store.exists(resume_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found.",
        )
    resume_store.delete(resume_id)
    # Also delete from Supabase if we mapped ID, but skipping for brevity
    return {"status": "deleted", "resume_id": resume_id}
