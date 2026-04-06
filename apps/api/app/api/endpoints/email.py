from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.email_service import EmailService

router = APIRouter()
email_service = EmailService()

class EmailSendRequest(BaseModel):
    recipientEmail: str
    subject: str
    body: str

@router.post("/send")
async def send_application_email(request: EmailSendRequest):
    """
    Optional endpoint to send an application email via SMTP.
    If EMAIL_USER/EMAIL_PASS are missing, it succeeds silently.
    """
    success = email_service.send_email(
        recipient=request.recipientEmail,
        subject=request.subject,
        body=request.body
    )
    
    if success:
        return {"status": "success", "message": "Email sent successfully (or mocked if no credentials)."}
    else:
        raise HTTPException(status_code=500, detail="Failed to send secure email via SMTP.")
