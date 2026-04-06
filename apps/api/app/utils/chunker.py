"""
utils/chunker.py — Text chunking utility for RAG (Phase 4).
Splits long resume text into overlapping chunks for FAISS indexing.
Supports character-based and sentence-aware chunking strategies.
"""

from typing import List
from app.core.logger import get_logger

logger = get_logger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> List[str]:
    """
    Split text into overlapping chunks for vector indexing.

    Args:
        text: Full resume text.
        chunk_size: Max characters per chunk.
        overlap: Overlap characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    chunks: List[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            if boundary != -1 and boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start >= len(text):
            break

    logger.debug(f"Chunked text into {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")
    return chunks


def chunk_by_sections(text: str) -> List[str]:
    """
    Split resume text by common section headers.
    Useful for more semantically meaningful RAG chunks.
    """
    import re
    section_headers = [
        r"(?i)(education|academic)",
        r"(?i)(experience|work history|employment)",
        r"(?i)(skills|technical skills|competencies)",
        r"(?i)(projects|personal projects)",
        r"(?i)(certifications|certificates)",
        r"(?i)(summary|objective|profile)",
        r"(?i)(achievements|awards|honors)",
    ]

    pattern = "|".join(f"({h})" for h in section_headers)
    parts = re.split(pattern, text)
    chunks = [p.strip() for p in parts if p and p.strip() and len(p.strip()) > 30]
    logger.debug(f"Section-split into {len(chunks)} chunks")
    return chunks if chunks else [text]
