"""
services/cover_letter_service.py — Cover Letter Generator (Phase 3 + Phase 4 RAG).
Uses a structured prompt template + LLM to generate personalized cover letters.
Optionally augments prompts with RAG-retrieved resume chunks for richer context.
"""

from typing import Optional, List
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService
from app.models.schemas import ParsedResume, CoverLetterRequest, CoverLetterResponse
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an expert career coach and professional writer specializing in 
internship and job applications. You write compelling, authentic, and personalized cover letters 
that highlight the candidate's genuine strengths and alignment with the role. 
Keep the letter concise (3-4 paragraphs), professional, and tailored to the specific opportunity.
Do NOT use generic filler phrases. Make every sentence count."""


def build_cover_letter_prompt(
    resume: ParsedResume,
    job_description: str,
    company_name: Optional[str],
    job_title: Optional[str],
    tone: str,
    rag_chunks: Optional[List[str]] = None,
) -> str:
    """
    Construct the structured prompt for cover letter generation.
    Injects resume data, job context, tone, and optional RAG chunks.
    """
    # Format resume data
    skills_str = ", ".join(resume.skills[:15]) if resume.skills else "Not specified"
    edu_str = ""
    if resume.education:
        edu = resume.education[0]
        edu_str = f"{edu.degree or ''} from {edu.institution or ''} ({edu.year or ''})".strip(", ()")

    exp_str = ""
    if resume.experience:
        exp_entries = []
        for e in resume.experience[:2]:
            entry = f"- {e.title or 'Role'} at {e.company or 'Company'}"
            exp_entries.append(entry)
        exp_str = "\n".join(exp_entries)

    # RAG context block
    rag_context = ""
    if rag_chunks:
        rag_context = "\n\n=== Additional Resume Context ===\n" + "\n---\n".join(rag_chunks[:3])

    # Tone instruction
    tone_map = {
        "professional": "formal, polished, and confident",
        "enthusiastic": "energetic, passionate, and forward-looking",
        "concise": "brief, direct, and impactful (keep under 250 words)",
    }
    tone_instruction = tone_map.get(tone.lower(), "professional and clear")

    prompt = f"""Write a cover letter with a {tone_instruction} tone.

=== CANDIDATE PROFILE ===
Name: {resume.name or "The Candidate"}
Email: {resume.email or "N/A"}
Top Skills: {skills_str}
Education: {edu_str or "Not specified"}
Relevant Experience:
{exp_str or "No experience listed"}
Summary: {resume.summary or "Not provided"}
{rag_context}

=== TARGET OPPORTUNITY ===
Company: {company_name or "the company"}
Role: {job_title or "the internship/position"}
Job Description:
{job_description[:1500]}

=== INSTRUCTIONS ===
1. Open with a strong hook referencing the specific role and company
2. Connect 2-3 specific skills/experiences from the resume to the job requirements
3. Show genuine enthusiasm for the company's mission or work
4. Close with a confident call-to-action

Write the complete cover letter now (no subject line needed, start with "Dear Hiring Manager,"):"""

    return prompt


class CoverLetterService:
    """Generates personalized cover letters using LLM + optional RAG."""

    def __init__(
        self,
        llm_service: LLMService,
        embedding_service: EmbeddingService,
        faiss_service: FAISSService,
    ):
        self.llm = llm_service
        self.embedder = embedding_service
        self.faiss = faiss_service

    def generate(
        self,
        resume_id: str,
        parsed_resume: ParsedResume,
        request: CoverLetterRequest,
    ) -> CoverLetterResponse:
        """
        Generate a personalized cover letter.

        Phase 4 RAG: If resume chunks are indexed, retrieve the top-K
        most relevant chunks to enrich the prompt context.
        """
        logger.info(f"Generating cover letter for resume '{resume_id}'")

        # Phase 4: Retrieve RAG chunks if indexed
        rag_chunks = []
        if self.faiss.namespace_exists(resume_id):
            query = f"{request.job_title or ''} {request.job_description[:200]}"
            query_vec = self.embedder.embed(query)
            results = self.faiss.search(resume_id, query_vec, top_k=settings.RAG_TOP_K)
            rag_chunks = [text for text, _ in results]
            logger.info(f"RAG retrieved {len(rag_chunks)} chunks for enrichment")

        # Build prompt
        prompt = build_cover_letter_prompt(
            resume=parsed_resume,
            job_description=request.job_description,
            company_name=request.company_name,
            job_title=request.job_title,
            tone=request.tone or "professional",
            rag_chunks=rag_chunks if rag_chunks else None,
        )

        # Generate via LLM
        cover_letter = self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1200,
        )

        word_count = len(cover_letter.split())

        return CoverLetterResponse(
            resume_id=resume_id,
            company_name=request.company_name,
            job_title=request.job_title,
            cover_letter=cover_letter,
            word_count=word_count,
        )
