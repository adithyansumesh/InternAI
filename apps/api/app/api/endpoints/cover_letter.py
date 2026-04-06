"""
api/endpoints/cover_letter.py — Phase 3: Cover Letter Generator.
POST /generate-cover-letter → Produces a personalized cover letter
using LLM + resume data + job description + optional RAG context.
"""

from fastapi import APIRouter, HTTPException, Depends, status

from app.core.dependencies import get_llm_service, get_embedding_service, get_faiss_service
from app.core.logger import get_logger
from app.models.schemas import CoverLetterRequest, CoverLetterResponse, ParsedResume
from app.models.store import resume_store
from app.services.cover_letter_service import CoverLetterService
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService

router = APIRouter()
logger = get_logger(__name__)


def get_cover_letter_service(
    llm: LLMService = Depends(get_llm_service),
    embedder: EmbeddingService = Depends(get_embedding_service),
    faiss: FAISSService = Depends(get_faiss_service),
) -> CoverLetterService:
    return CoverLetterService(
        llm_service=llm,
        embedding_service=embedder,
        faiss_service=faiss,
    )


@router.post(
    "/generate-cover-letter",
    response_model=CoverLetterResponse,
    summary="Generate a personalized cover letter",
    description=(
        "Generate a tailored cover letter using the candidate's parsed resume, "
        "the job description, and an LLM. If the resume has been RAG-indexed "
        "(Phase 4), relevant context is automatically retrieved and injected."
    ),
)
async def generate_cover_letter(
    request: CoverLetterRequest,
    cover_letter_svc: CoverLetterService = Depends(get_cover_letter_service),
):
    # Retrieve parsed resume from store
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

    # Check LLM availability
    if not cover_letter_svc.llm.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not available. Check OPENAI_API_KEY and install openai SDK.",
        )

    try:
        result = cover_letter_svc.generate(
            resume_id=request.resume_id,
            parsed_resume=parsed_resume,
            request=request,
        )
        return result

    except RuntimeError as e:
        logger.error(f"Cover letter generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM generation error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while generating cover letter.",
        )
