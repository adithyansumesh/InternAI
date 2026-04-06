from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from app.utils.pdf_generator import generate_resume_pdf
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

class PDFRequest(BaseModel):
    markdown_text: str
    filename: str = "InternAI_Resume.pdf"

@router.post("/generate")
async def generate_pdf_endpoint(request: PDFRequest):
    """
    Endpoint to convert a markdown resume to a PDF and return it as a download.
    """
    logger.info(f"Generating PDF for: {request.filename}")
    try:
        pdf_bytes = generate_resume_pdf(request.markdown_text)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            }
        )
    except Exception as e:
        logger.error(f"PDF Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
