"""
services/matching_service.py — Job Matching Engine (Phase 2).
Uses LLM-based matching instead of heavy embedding models.
This is optimized for low-memory environments like Render free tier.
"""

import json
import re
from typing import List, Tuple
from app.services.llm_service import LLMService
from app.models.schemas import ParsedResume, JobMatchResponse
from app.services.resume_parser import KNOWN_SKILLS
from app.core.logger import get_logger

logger = get_logger(__name__)


class MatchingService:
    """
    Orchestrates job-resume matching using LLM for scoring
    and keyword-based skill gap analysis.
    No heavy ML models needed.
    """

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def match(
        self,
        resume_id: str,
        parsed_resume: ParsedResume,
        job_description: str,
    ) -> JobMatchResponse:
        """
        Compute match between a resume and job description using
        skill overlap + LLM scoring.
        """
        logger.info(f"Matching resume '{resume_id}' against job description")

        # Step 1: Skill gap analysis (fast, no ML needed)
        resume_skills = {s.lower() for s in parsed_resume.skills}
        jd_skills = self._extract_skills_from_jd(job_description)

        matched_skills = sorted(resume_skills & jd_skills)
        missing_skills = sorted(jd_skills - resume_skills)

        # Step 2: Calculate score based on skill overlap
        if jd_skills:
            skill_score = len(matched_skills) / len(jd_skills) * 100
        else:
            skill_score = 50.0  # Default if no skills detected

        match_score = round(min(skill_score, 100.0), 2)

        # Step 3: Label and recommendation
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
