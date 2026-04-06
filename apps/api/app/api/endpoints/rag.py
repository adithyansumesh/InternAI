"""
api/endpoints/rag.py — Phase 4: RAG Enhancement.
Endpoints to:
  POST /rag/index  — Chunk and index a resume into FAISS
  POST /rag/query  — Retrieve top-K relevant chunks for a query
  GET  /rag/status/{resume_id} — Check if a resume has been indexed
"""

from fastapi import APIRouter, HTTPException, Depends, status

from app.core.dependencies import get_embedding_service, get_faiss_service
from app.core.logger import get_logger
from app.models.schemas import (
    RAGIndexRequest, RAGIndexResponse,
    RAGQueryRequest, RAGQueryResponse,
)
from app.models.store import resume_store
from app.services.rag_service import RAGService
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService

router = APIRouter()
logger = get_logger(__name__)


def get_rag_service(
    embedder: EmbeddingService = Depends(get_embedding_service),
    faiss: FAISSService = Depends(get_faiss_service),
) -> RAGService:
    return RAGService(embedding_service=embedder, faiss_service=faiss)


@router.post(
    "/index",
    response_model=RAGIndexResponse,
    summary="Index a resume for RAG retrieval",
    description=(
        "Chunk the resume text into overlapping segments, embed them, "
        "and store in FAISS. Required before cover letter generation can "
        "leverage RAG enhancement."
    ),
)
async def index_resume(
    request: RAGIndexRequest,
    rag_svc: RAGService = Depends(get_rag_service),
):
    parsed_resume = resume_store.get(request.resume_id)
    if not parsed_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{request.resume_id}' not found.",
        )

    try:
        result = rag_svc.index_resume(
            resume_id=request.resume_id,
            parsed_resume=parsed_resume,
        )
        return result
    except Exception as e:
        logger.error(f"RAG indexing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG indexing error: {str(e)}",
        )


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    summary="Query indexed resume chunks",
    description="Retrieve the most semantically relevant resume chunks for a given query.",
)
async def query_resume(
    request: RAGQueryRequest,
    rag_svc: RAGService = Depends(get_rag_service),
):
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    try:
        result = rag_svc.query(request)
        return result
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query error: {str(e)}",
        )


@router.get(
    "/status/{resume_id}",
    summary="Check RAG index status for a resume",
)
async def rag_status(
    resume_id: str,
    rag_svc: RAGService = Depends(get_rag_service),
):
    is_indexed = rag_svc.is_indexed(resume_id)
    chunk_count = rag_svc.faiss.get_vector_count(resume_id) if is_indexed else 0
    return {
        "resume_id": resume_id,
        "indexed": is_indexed,
        "chunks": chunk_count,
    }
