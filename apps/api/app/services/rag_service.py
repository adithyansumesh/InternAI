"""
services/rag_service.py — RAG Enhancement Service (Phase 4).
Chunks resume text and stores embeddings in FAISS for retrieval-augmented generation.
Retrieves semantically relevant resume chunks before LLM calls.
"""

from typing import List, Tuple
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService
from app.utils.chunker import chunk_text
from app.models.schemas import (
    ParsedResume, RAGIndexRequest, RAGIndexResponse,
    RAGQueryRequest, RAGQueryResponse,
)
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RAGService:
    """
    Handles the full RAG pipeline:
    1. Chunk resume text
    2. Embed chunks
    3. Store in FAISS under resume's namespace
    4. Retrieve top-K chunks for a given query
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        faiss_service: FAISSService,
    ):
        self.embedder = embedding_service
        self.faiss = faiss_service

    def index_resume(
        self,
        resume_id: str,
        parsed_resume: ParsedResume,
    ) -> RAGIndexResponse:
        """
        Chunk the resume text and index all chunks into FAISS.

        Args:
            resume_id: Unique identifier for the resume (used as FAISS namespace)
            parsed_resume: Parsed resume object containing raw text

        Returns:
            RAGIndexResponse with status and chunk count
        """
        logger.info(f"Indexing resume '{resume_id}' for RAG")
        raw_text = parsed_resume.raw_text

        if not raw_text.strip():
            return RAGIndexResponse(
                resume_id=resume_id,
                chunks_indexed=0,
                status="error: empty resume text",
            )

        # Step 1: Chunk the text
        chunks = chunk_text(
            text=raw_text,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )

        if not chunks:
            return RAGIndexResponse(
                resume_id=resume_id,
                chunks_indexed=0,
                status="error: no chunks generated",
            )

        # Step 2: Batch embed chunks
        vectors = self.embedder.embed_batch(chunks)

        # Step 3: Store in FAISS under resume's namespace
        count = self.faiss.add_vectors(
            namespace=resume_id,
            vectors=vectors,
            texts=chunks,
        )

        logger.info(f"Indexed {count} chunks for resume '{resume_id}'")
        return RAGIndexResponse(
            resume_id=resume_id,
            chunks_indexed=count,
            status="success",
        )

    def query(
        self,
        request: RAGQueryRequest,
    ) -> RAGQueryResponse:
        """
        Retrieve top-K relevant chunks from the indexed resume.

        Args:
            request: Contains resume_id, query string, and top_k

        Returns:
            RAGQueryResponse with retrieved chunks and similarity scores
        """
        logger.info(f"RAG query for resume '{request.resume_id}': '{request.query[:60]}'")

        if not self.faiss.namespace_exists(request.resume_id):
            # Try loading from disk
            loaded = self.faiss.load_index(request.resume_id)
            if not loaded:
                return RAGQueryResponse(
                    resume_id=request.resume_id,
                    query=request.query,
                    retrieved_chunks=["Resume not indexed. Call POST /rag/index first."],
                    scores=[0.0],
                )

        query_vec = self.embedder.embed(request.query)
        results: List[Tuple[str, float]] = self.faiss.search(
            namespace=request.resume_id,
            query_vector=query_vec,
            top_k=request.top_k,
        )

        chunks = [r[0] for r in results]
        scores = [round(r[1], 4) for r in results]

        return RAGQueryResponse(
            resume_id=request.resume_id,
            query=request.query,
            retrieved_chunks=chunks,
            scores=scores,
        )

    def is_indexed(self, resume_id: str) -> bool:
        return self.faiss.namespace_exists(resume_id)
