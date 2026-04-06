"""
services/matching_service.py — Job Matching Engine (Phase 2).
Computes semantic similarity between resume and job description using
vector embeddings and cosine similarity via FAISS.
Also performs skill gap analysis to identify missing skills.
"""

from typing import List, Tuple
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService
from app.models.schemas import ParsedResume, JobMatchResponse
from app.services.resume_parser import KNOWN_SKILLS
from app.core.logger import get_logger
import re

logger = get_logger(__name__)


class MatchingService:
    """
    Orchestrates job-resume matching:
    1. Embed both texts
    2. Compute cosine similarity
    3. Perform skill gap analysis
    4. Return structured MatchResponse
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        faiss_service: FAISSService,
    ):
        self.embedder = embedding_service
        self.faiss = faiss_service

    def match(
        self,
        resume_id: str,
        parsed_resume: ParsedResume,
        job_description: str,
    ) -> JobMatchResponse:
        """
        Compute match between a resume and job description.

        Returns:
            JobMatchResponse with score, missing skills, and recommendation.
        """
        logger.info(f"Matching resume '{resume_id}' against job description")

        # Step 1: Generate embeddings
        resume_vec = self.embedder.embed(parsed_resume.raw_text)
        jd_vec = self.embedder.embed(job_description)

        # Step 2: Cosine similarity score (0–1 → percentage)
        raw_score = self.embedder.cosine_similarity(resume_vec, jd_vec)
        match_score = round(raw_score * 100, 2)

        # Step 3: Skill gap analysis
        resume_skills = {s.lower() for s in parsed_resume.skills}
        jd_skills = self._extract_skills_from_jd(job_description)

        matched_skills = sorted(resume_skills & jd_skills)
        missing_skills = sorted(jd_skills - resume_skills)

        # Step 4: Store in FAISS for future retrieval (global index)
        self.faiss.add_vectors("global_jd", jd_vec.reshape(1, -1), [job_description[:200]])

        # Step 5: Label and recommendation
        label, recommendation = self._score_label(match_score, len(missing_skills))

        return JobMatchResponse(
            resume_id=resume_id,
            match_score=match_score,
            match_label=label,
            missing_skills=missing_skills,
            matched_skills=matched_skills,
            recommendation=recommendation,
        )

    def _extract_skills_from_jd(self, jd_text: str) -> set:
        """Extract known skills mentioned in the job description."""
        jd_lower = jd_text.lower()
        found = set()
        for skill in KNOWN_SKILLS:
            if re.search(r"\b" + re.escape(skill) + r"\b", jd_lower):
                found.add(skill)
        return found

    def _score_label(self, score: float, missing_count: int) -> Tuple[str, str]:
        """Map match score to human-readable label and recommendation."""
        if score >= 80:
            return (
                "Excellent Match ✅",
                "Your profile is highly aligned. Apply with confidence!"
            )
        elif score >= 60:
            return (
                "Good Match 👍",
                f"Strong fit! Consider addressing {missing_count} missing skill(s) before applying."
            )
        elif score >= 40:
            return (
                "Fair Match ⚠️",
                f"Partial match. Work on {missing_count} skill gap(s) to increase your chances."
            )
        else:
            return (
                "Low Match ❌",
                f"Significant skill gaps ({missing_count} skills). "
                "Consider upskilling or targeting better-matched roles."
            )
