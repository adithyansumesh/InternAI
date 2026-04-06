"""
main.py — Application entry point.
Initializes FastAPI app, registers routers, configures CORS, and mounts middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import resume, matching, cover_letter, rag, profile, auth, internships, workflow, analyze, email, pdf
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    logger.info("🚀 Starting AI Internship Discovery Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("🛑 Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Driven Internship Discovery and Application Automation using NLP",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Phase 0 – Auth"])
app.include_router(internships.router, prefix="/api/v1/internships", tags=["Phase 0 – Internships"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Phase 1 – Resume Intelligence"])
app.include_router(matching.router, prefix="/api/v1/match", tags=["Phase 2 – Job Matching Engine"])
app.include_router(cover_letter.router, prefix="/api/v1/cover-letter", tags=["Phase 3 – Cover Letter Generator"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["Phase 4 – RAG Enhancement"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Phase 5 – Automation Profile"])
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["Phase 7 – Multi-Agent Orchestrator"])
app.include_router(email.router, prefix="/api/v1/email", tags=["Phase 8 – Application Automation"])
app.include_router(pdf.router, prefix="/api/v1/pdf", tags=["PDF Generation"])
app.include_router(analyze.router, prefix="", tags=["Unified Analysis"])

@app.get("/", tags=["Health"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "InternAI Backend"}
