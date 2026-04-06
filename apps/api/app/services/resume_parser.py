"""
services/resume_parser.py — Resume parsing service.
Transforms raw resume text into structured JSON using spaCy NLP + regex heuristics.
Extracts: name, email, phone, skills, education, experience, summary.
"""

import re
from typing import List, Optional, Dict
from app.services.nlp_service import NLPService
from app.models.schemas import ParsedResume, EducationEntry, ExperienceEntry
from app.core.logger import get_logger

logger = get_logger(__name__)

# Curated tech/professional skills vocabulary
KNOWN_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "sql",
    # Web / Frameworks
    "react", "vue", "angular", "node.js", "express", "django", "flask",
    "fastapi", "spring", "laravel", "nextjs", "html", "css", "graphql", "rest",
    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
    "hugging face", "transformers", "langchain", "llm", "rag",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "terraform", "ansible", "git", "github", "linux",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
    "dynamodb", "cassandra",
    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving",
    "project management", "agile", "scrum",
}

DEGREE_KEYWORDS = [
    "bachelor", "master", "phd", "b.s.", "m.s.", "b.e.", "m.e.", "b.tech",
    "m.tech", "mba", "associate", "diploma", "b.sc", "m.sc", "doctor",
    "undergraduate", "graduate",
]

SECTION_HEADERS = {
    "experience": r"(work experience|experience|employment|professional background|internships?)",
    "education": r"(education|academic|qualification|schooling)",
    "skills": r"(skills|technical skills|competencies|technologies|tools)",
    "summary": r"(summary|objective|profile|about me|about)",
    "projects": r"(projects|personal projects|academic projects)",
    "certifications": r"(certifications?|certificates?|credentials?|licenses?)",
}


class ResumeParserService:
    """Orchestrates resume parsing from raw text → structured ParsedResume."""

    def __init__(self, nlp_service: NLPService):
        self.nlp = nlp_service
        logger.info("ResumeParserService initialized")

    def parse(self, raw_text: str) -> ParsedResume:
        """Main entry point: parse raw text into structured ParsedResume."""
        logger.info(f"Parsing resume ({len(raw_text)} chars)")

        sections = self._split_sections(raw_text)

        name = self.nlp.extract_name(raw_text)
        email = self.nlp.extract_email(raw_text)
        phone = self.nlp.extract_phone(raw_text)
        skills = self._extract_skills(sections.get("skills", "") or raw_text)
        education = self._extract_education(sections.get("education", ""))
        experience = self._extract_experience(sections.get("experience", ""))
        summary = self._extract_summary(sections.get("summary", ""))

        parsed = ParsedResume(
            raw_text=raw_text,
            name=name,
            email=email,
            phone=phone,
            skills=skills,
            education=education,
            experience=experience,
            summary=summary,
        )

        logger.info(
            f"Parsed: name={name}, email={email}, "
            f"skills={len(skills)}, edu={len(education)}, exp={len(experience)}"
        )
        return parsed

    def _split_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into named sections using header detection."""
        sections: Dict[str, str] = {}
        lines = text.split("\n")
        current_section = "header"
        buffer: List[str] = []

        for line in lines:
            stripped = line.strip()
            matched_section = self._detect_section_header(stripped)

            if matched_section:
                if buffer:
                    sections[current_section] = "\n".join(buffer).strip()
                current_section = matched_section
                buffer = []
            else:
                buffer.append(line)

        if buffer:
            sections[current_section] = "\n".join(buffer).strip()

        return sections

    def _detect_section_header(self, line: str) -> Optional[str]:
        """Check if a line is a known section header."""
        if not line or len(line) > 60:
            return None
        for section, pattern in SECTION_HEADERS.items():
            if re.match(pattern, line.strip(), re.IGNORECASE):
                return section
        return None

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills by matching against known skills vocabulary."""
        if not text:
            return []

        text_lower = text.lower()
        found = set()

        for skill in KNOWN_SKILLS:
            if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
                found.add(skill.title() if len(skill) > 4 else skill.upper())

        # Also extract comma/pipe separated tokens from skills section
        tokens = re.split(r"[,|•\n/]", text)
        for token in tokens:
            token = token.strip()
            if 2 < len(token) < 40 and token.lower() in KNOWN_SKILLS:
                found.add(token)

        return sorted(found)

    def _extract_education(self, text: str) -> List[EducationEntry]:
        """Parse education entries from the education section."""
        if not text:
            return []

        entries: List[EducationEntry] = []
        blocks = re.split(r"\n{2,}", text)

        for block in blocks:
            if not block.strip():
                continue

            degree = None
            institution = None
            year = None

            # Look for degree
            for kw in DEGREE_KEYWORDS:
                if re.search(r"\b" + kw + r"\b", block, re.IGNORECASE):
                    degree_match = re.search(
                        r"(bachelor[^\n,]*|master[^\n,]*|phd[^\n,]*|b\.[^\n,]*|m\.[^\n,]*)",
                        block, re.IGNORECASE
                    )
                    if degree_match:
                        degree = degree_match.group(0).strip()
                    break

            # Look for year (4-digit)
            year_match = re.search(r"\b(19|20)\d{2}\b", block)
            if year_match:
                year = year_match.group(0)

            # Try institution from NLP entities
            entities = self.nlp.extract_entities(block)
            orgs = entities.get("ORG", [])
            if orgs:
                institution = orgs[0]
            else:
                # Fallback: look for "University", "College", "Institute"
                inst_match = re.search(
                    r"([A-Z][a-z]+(?: [A-Z][a-z]+)* (?:University|College|Institute|School|Academy))",
                    block
                )
                if inst_match:
                    institution = inst_match.group(0)

            if degree or institution:
                entries.append(EducationEntry(degree=degree, institution=institution, year=year))

        return entries or []

    def _extract_experience(self, text: str) -> List[ExperienceEntry]:
        """Parse work/internship experience entries."""
        if not text:
            return []

        entries: List[ExperienceEntry] = []
        blocks = re.split(r"\n{2,}", text)

        for block in blocks:
            block = block.strip()
            if len(block) < 20:
                continue

            title = None
            company = None
            duration = None
            description = block

            # Extract duration patterns
            duration_match = re.search(
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}"
                r"\s*[-–]\s*"
                r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|Present|Current)",
                block, re.IGNORECASE
            )
            if duration_match:
                duration = duration_match.group(0)

            # NLP entities for org
            entities = self.nlp.extract_entities(block)
            orgs = entities.get("ORG", [])
            if orgs:
                company = orgs[0]

            # Extract job title from first line
            first_line = block.split("\n")[0].strip()
            job_title_patterns = [
                r"(intern|engineer|developer|analyst|manager|consultant|designer|scientist|"
                r"associate|coordinator|specialist|lead|director|researcher)",
            ]
            for pat in job_title_patterns:
                if re.search(pat, first_line, re.IGNORECASE):
                    title = first_line[:80]
                    break

            if title or company:
                entries.append(ExperienceEntry(
                    title=title,
                    company=company,
                    duration=duration,
                    description=description[:300] if description else None,
                ))

        return entries or []

    def _extract_summary(self, text: str) -> Optional[str]:
        """Return a cleaned summary/objective section."""
        if not text:
            return None
        # Return first 500 chars of summary section
        return text.strip()[:500] if text.strip() else None
