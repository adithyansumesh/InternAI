"""
utils/pdf_extractor.py — PDF text extraction utility.
Uses pdfplumber for reliable text extraction from uploaded PDF resumes.
Falls back to PyPDF2 if pdfplumber fails on a specific page.
"""

import io
from typing import Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file given its raw bytes.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If text extraction fails or PDF is empty/unreadable.
    """
    text_parts = []

    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
                    logger.debug(f"Extracted page {i + 1}: {len(page_text)} chars")

        full_text = "\n\n".join(text_parts).strip()

        if not full_text:
            raise ValueError("No extractable text found in PDF. It may be scanned/image-based.")

        logger.info(f"PDF extraction complete: {len(full_text)} total characters")
        return full_text

    except ImportError:
        logger.warning("pdfplumber not available, falling back to PyPDF2")
        return _extract_with_pypdf2(file_bytes)

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def _extract_with_pypdf2(file_bytes: bytes) -> str:
    """Fallback extractor using PyPDF2."""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(p.strip() for p in pages if p.strip())
        if not text:
            raise ValueError("PyPDF2 also returned empty text.")
        return text
    except Exception as e:
        raise ValueError(f"Both pdfplumber and PyPDF2 failed: {str(e)}")
