"""
api/endpoints/matching.py — Job Matching Engine.
Accepts a resume_id + job description and returns match results.
"""

from fastapi import APIRouter, HTTPException, Depends, status

from app.core.dependencies import get_llm_service
from app.core.logger import get_logger
from app.models.schemas import JobMatchRequest, JobMatchResponse
from app.services.matching_service import MatchingService
from app.services.llm_service import LLMService
from app.models.store import resume_store

router = APIRouter()
logger = get_logger(__name__)


def get_matching_service(
    llm: LLMService = Depends(get_llm_service),
) -> MatchingService:
    return MatchingService(llm)


@router.post(
    "/",
    response_model=JobMatchResponse,
    summary="Match a resume against a job description",
)
async def match_resume_to_job(
    request: JobMatchRequest,
    matching_svc: MatchingService = Depends(get_matching_service),
):
    parsed_resume = resume_store.get(request.resume_id)
    if not parsed_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{request.resume_id}' not found. Upload via POST /resume/upload first.",
        )

    if not request.job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="job_description cannot be empty.",
        )

    try:
        result = matching_svc.match(
            resume_id=request.resume_id,
            parsed_resume=parsed_resume,
            job_description=request.job_description,
        )
        return result

    except Exception as e:
        logger.error(f"Matching failed for resume '{request.resume_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching engine error: {str(e)}",
        )
