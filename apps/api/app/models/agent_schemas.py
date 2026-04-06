from pydantic import BaseModel, Field
from typing import List, Optional

class CategorizedSkills(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    ai_ml_skills: List[str] = Field(default_factory=list)
    tools_frameworks: List[str] = Field(default_factory=list)

class InternshipListing(BaseModel):
    role: str
    company: str
    location: str
    description: str
    application_link: str

class MatchEvaluation(BaseModel):
    match_score: int = Field(ge=1, le=10)
    reasoning: str
    recommendation: str

class JobApplicationData(BaseModel):
    internship: InternshipListing
    match_evaluation: MatchEvaluation
    cover_letter: Optional[str] = None
    tailored_resume: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None

class FinalApplicationPackage(BaseModel):
    resume_id: str
    categorized_skills: CategorizedSkills
    applications: List[JobApplicationData]

class ApplicationGenerationRequest(BaseModel):
    resume_id: str
    internship: InternshipListing
    match_score: int
    reasoning: str

class GeneratedMaterialsResponse(BaseModel):
    application_id: Optional[str] = None
    cover_letter: Optional[str] = None
    tailored_resume: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


class UpdateGeneratedMaterialsRequest(BaseModel):
    application_id: str
    tailored_resume: Optional[str] = None
    cover_letter: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
