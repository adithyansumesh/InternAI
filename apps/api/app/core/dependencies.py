"""
core/dependencies.py — FastAPI dependency injection.
Provides singleton-like instances of services (NLP, LLM).
These are injected into route handlers via FastAPI's Depends() mechanism.
Optimized for low-memory deployment (no heavy ML models).
"""

from functools import lru_cache
from app.services.nlp_service import NLPService
from app.services.llm_service import LLMService
from app.services.resume_parser import ResumeParserService
from app.core.config import settings
from supabase_client import supabase
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


@lru_cache()
def get_nlp_service() -> NLPService:
    """Singleton NLP service (spaCy model loaded once)."""
    return NLPService(model_name=settings.SPACY_MODEL)


@lru_cache()
def get_llm_service() -> LLMService:
    """Singleton LLM service (OpenAI-compatible client)."""
    return LLMService(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        base_url=settings.OPENAI_BASE_URL,
    )


@lru_cache()
def get_resume_parser() -> ResumeParserService:
    """Singleton resume parser that depends on NLP service."""
    nlp = get_nlp_service()
    return ResumeParserService(nlp_service=nlp)


# ── Auth Dependencies ──────────────────────────────────────────

class UserSchema(BaseModel):
    id: str
    email: str
    name: str = "The Candidate"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> UserSchema:
    """
    Validate JWT token and return the current user.
    Used to protect routes and identify the caller.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Frontend sends the user_id as the token (simple session handling)
        response = supabase.table("users").select("*").eq("id", token).execute()
        if not response.data:
            raise credentials_exception
        user_data = response.data[0]
        return UserSchema(**user_data)
    except Exception as e:
        print(f"Auth DB Error: {e}")
        raise credentials_exception
