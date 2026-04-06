"""
models/schemas.py — All Pydantic request/response schemas.
Defines the data contracts for every API endpoint across all 5 phases.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ─────────────────────────────────────────────
# PHASE 0 — Authentication
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: str
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class UserOut(BaseModel):
    id: str
    email: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PHASE 1 — Resume Intelligence
# ─────────────────────────────────────────────

class EducationEntry(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    field_of_study: Optional[str] = None


class ExperienceEntry(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class ParsedResume(BaseModel):
    raw_text: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    summary: Optional[str] = None


class ResumeUploadResponse(BaseModel):
    status: str
    filename: str
    resume_id: str
    parsed: ParsedResume


# ─────────────────────────────────────────────
# PHASE 2 — Job Matching Engine
# ─────────────────────────────────────────────

class JobMatchRequest(BaseModel):
    resume_id: str = Field(..., description="ID returned from resume upload")
    job_description: str = Field(..., description="Full job description text")


class JobMatchResponse(BaseModel):
    resume_id: str
    match_score: float = Field(..., description="Cosine similarity score as percentage")
    match_label: str = Field(..., description="Excellent / Good / Fair / Low")
    missing_skills: List[str]
    matched_skills: List[str]
    recommendation: str


# ─────────────────────────────────────────────
# PHASE 3 — Cover Letter Generator
# ─────────────────────────────────────────────

class CoverLetterRequest(BaseModel):
    resume_id: str = Field(..., description="ID returned from resume upload")
    job_description: str = Field(..., description="Full job description text")
    company_name: Optional[str] = Field(None, description="Target company name")
    job_title: Optional[str] = Field(None, description="Target job title")
    tone: Optional[str] = Field("professional", description="Tone: professional / enthusiastic / concise")


class CoverLetterResponse(BaseModel):
    resume_id: str
    company_name: Optional[str]
    job_title: Optional[str]
    cover_letter: str
    word_count: int


# ─────────────────────────────────────────────
# PHASE 4 — RAG Enhancement
# ─────────────────────────────────────────────

class RAGIndexRequest(BaseModel):
    resume_id: str = Field(..., description="Resume ID to chunk and index")


class RAGIndexResponse(BaseModel):
    resume_id: str
    chunks_indexed: int
    status: str


class RAGQueryRequest(BaseModel):
    resume_id: str
    query: str = Field(..., description="Query to retrieve relevant resume chunks")
    top_k: int = Field(3, ge=1, le=10)


class RAGQueryResponse(BaseModel):
    resume_id: str
    query: str
    retrieved_chunks: List[str]
    scores: List[float]


# ─────────────────────────────────────────────
# PHASE 6 — Internship Management & Tracking
# ─────────────────────────────────────────────

class InternshipResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    required_skills: List[str]

    class Config:
        from_attributes = True

class SavedInternshipOut(BaseModel):
    id: int
    internship_id: int
    internship: InternshipResponse
    saved_at: datetime

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    internship_id: int
    resume_id: str
    cover_letter: Optional[str] = None

class ApplicationOut(BaseModel):
    id: int
    internship: InternshipResponse
    status: str
    applied_at: datetime
    cover_letter: Optional[str] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PHASE 5 — Automation & Profile
# ─────────────────────────────────────────────

class AutofillProfile(BaseModel):
    resume_id: str
    personal_info: Dict[str, Optional[str]]
    skills: List[str]
    education: List[EducationEntry]
    experience: List[ExperienceEntry]
    autofill_fields: Dict[str, Any]


# ─────────────────────────────────────────────
# Shared
# ─────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
