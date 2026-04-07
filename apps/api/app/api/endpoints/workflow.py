from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.logger import get_logger
from app.models.agent_schemas import FinalApplicationPackage
from app.models.store import resume_store
from app.agents.workflow import ApplicationWorkflow
from app.core.dependencies import get_llm_service
from app.services.matching_service import MatchingService
from app.services.cover_letter_service import CoverLetterService
from app.agents.resume_tailor_agent import ResumeTailorAgent
from app.agents.email_agent import EmailAgent

logger = get_logger(__name__)
router = APIRouter()

class WorkflowRunRequest(BaseModel):
    resume_id: str
    preferred_field: str
    location: str

def get_matching_service(
    llm_svc=Depends(get_llm_service),
) -> MatchingService:
    return MatchingService(llm_svc)

def get_cover_letter_service(
    llm_svc=Depends(get_llm_service),
) -> CoverLetterService:
    return CoverLetterService(llm_svc)

def get_application_workflow(
    llm=Depends(get_llm_service),
    matcher=Depends(get_matching_service),
    cover_letter_gen=Depends(get_cover_letter_service)
) -> ApplicationWorkflow:
    resume_tailor = ResumeTailorAgent(llm)
    email_agent = EmailAgent(llm)
    return ApplicationWorkflow(llm, matcher, cover_letter_gen, resume_tailor, email_agent)

@router.post("/run", response_model=FinalApplicationPackage)
async def run_workflow(
    request: WorkflowRunRequest,
    workflow: ApplicationWorkflow = Depends(get_application_workflow)
):
    """
    Executes the multi-agent Application Discovery and Application Workflow.
    """
    logger.info(f"Triggered workflow run for resume: {request.resume_id}")
    
    parsed_resume = resume_store.get(request.resume_id)
    if not parsed_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{request.resume_id}' not found. Please upload first."
        )

    try:
        package = workflow.run_discovery(
            resume_id=request.resume_id,
            parsed_resume=parsed_resume,
            preferred_field=request.preferred_field,
            location=request.location
        )
        return package
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")
