"""
api/endpoints/matching.py — Phase 2: Job Matching Engine.
Accepts a resume_id + job description and returns:
- Semantic similarity score (%)
- Matched and missing skills
- Recommendation label
"""

from fastapi import APIRouter, HTTPException, Depends, status

from app.core.dependencies import get_embedding_service, get_faiss_service
from app.core.logger import get_logger
from app.models.schemas import JobMatchRequest, JobMatchResponse, ParsedResume
from app.services.matching_service import MatchingService
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService
from app.models.store import resume_store

router = APIRouter()
logger = get_logger(__name__)


def get_matching_service(
    embedder: EmbeddingService = Depends(get_embedding_service),
    faiss: FAISSService = Depends(get_faiss_service),
) -> MatchingService:
    return MatchingService(embedding_service=embedder, faiss_service=faiss)


@router.post(
    "/",
    response_model=JobMatchResponse,
    summary="Match a resume against a job description",
    description=(
        "Provide a resume_id (from /resume/upload) and a job description. "
        "Returns a semantic match score, skill gaps, and actionable recommendations."
    ),
)
async def match_resume_to_job(
    request: JobMatchRequest,
    matching_svc: MatchingService = Depends(get_matching_service),
):
    # Retrieve parsed resume from memory store
    parsed_resume = resume_store.get(request.resume_id)
    if not parsed_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{request.resume_id}' not found. Upload via POST /resume/upload first.",
        )
    # Ensure raw_text is attached if service needs it (MatchingService uses raw_text from schema or argument)
    # The schema might need update or we pass raw_text explicitly.
    # Looking at MatchingService.match, it uses parsed_resume.raw_text and also passed job_description.

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
