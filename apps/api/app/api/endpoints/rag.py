"""
api/endpoints/rag.py — RAG Enhancement (disabled for lightweight deployment).
These endpoints are placeholders since RAG requires heavy embedding models.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post("/index")
async def index_resume():
    """RAG indexing is disabled in lightweight deployment mode."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="RAG indexing is not available in lightweight deployment mode.",
    )


@router.post("/query")
async def query_resume():
    """RAG query is disabled in lightweight deployment mode."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="RAG query is not available in lightweight deployment mode.",
    )


@router.get("/status/{resume_id}")
async def rag_status(resume_id: str):
    return {
        "resume_id": resume_id,
        "indexed": False,
        "chunks": 0,
    }
