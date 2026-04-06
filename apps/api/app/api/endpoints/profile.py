"""
api/endpoints/profile.py — Phase 5: Automation Layer.
Provides a structured autofill profile for browser automation tools.
The profile maps parsed resume fields to common form field names
(e.g., LinkedIn Easy Apply, Greenhouse, Lever, Workday, etc.)

NOTE: Full browser automation (Playwright/Selenium) is scaffolded but not
implemented here. This API gives the automation layer all data it needs.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.logger import get_logger
from app.models.schemas import AutofillProfile
from app.models.store import resume_store

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/{resume_id}",
    response_model=AutofillProfile,
    summary="Get structured autofill profile for browser automation",
    description=(
        "Returns a flat key-value autofill profile derived from the parsed resume. "
        "Designed for integration with browser automation tools (Playwright, Selenium, "
        "or Chrome Extension content scripts)."
    ),
)
async def get_autofill_profile(resume_id: str):
    """
    Build and return an autofill-ready profile from a parsed resume.
    Field names match common ATS form fields.
    """
    parsed = resume_store.get(resume_id)
    if not parsed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found. Upload via POST /resume/upload first.",
        )

    # Flatten education
    edu = parsed.education[0] if parsed.education else None
    # Flatten experience
    exp = parsed.experience[0] if parsed.experience else None
    skills_csv = ", ".join(parsed.skills) if parsed.skills else ""

    # Standard ATS field mapping
    autofill_fields = {
        # Personal
        "first_name": _first_name(parsed.name),
        "last_name": _last_name(parsed.name),
        "full_name": parsed.name,
        "email": parsed.email,
        "phone": parsed.phone,

        # Education
        "school": edu.institution if edu else None,
        "degree": edu.degree if edu else None,
        "graduation_year": edu.year if edu else None,
        "field_of_study": edu.field_of_study if edu else None,

        # Experience
        "current_title": exp.title if exp else None,
        "current_company": exp.company if exp else None,

        # Skills
        "skills": skills_csv,

        # Summary
        "cover_summary": parsed.summary,

        # LinkedIn / portfolio placeholders
        "linkedin_url": "",
        "portfolio_url": "",
        "github_url": "",
    }

    personal_info = {
        "name": parsed.name,
        "email": parsed.email,
        "phone": parsed.phone,
    }

    logger.info(f"Autofill profile built for resume '{resume_id}'")

    return AutofillProfile(
        resume_id=resume_id,
        personal_info=personal_info,
        skills=parsed.skills,
        education=parsed.education,
        experience=parsed.experience,
        autofill_fields=autofill_fields,
    )


@router.get(
    "/{resume_id}/automation-schema",
    summary="Get automation integration schema",
    description=(
        "Returns the schema structure for integrating with browser extension "
        "content scripts or Playwright-based automation."
    ),
)
async def get_automation_schema(resume_id: str):
    """
    Returns a schema blueprint showing how to wire the autofill profile
    to common job application platforms.
    """
    return {
        "resume_id": resume_id,
        "supported_platforms": [
            "LinkedIn Easy Apply",
            "Greenhouse",
            "Lever",
            "Workday",
            "iCIMS",
            "Taleo",
            "BambooHR",
        ],
        "integration_options": {
            "browser_extension": {
                "method": "Content script reads /profile/{resume_id} and fills form fields",
                "trigger": "User clicks 'AutoFill' button in extension popup",
                "autofill_endpoint": f"/api/v1/profile/{resume_id}",
            },
            "playwright_automation": {
                "method": "Python Playwright script fetches profile and fills forms",
                "example_script": "scripts/autofill_playwright.py",
            },
            "webhook": {
                "method": "POST autofill_fields to a Chrome Native Messaging endpoint",
                "payload_endpoint": f"/api/v1/profile/{resume_id}",
            },
        },
        "field_mapping_docs": (
            "See autofill_fields in GET /api/v1/profile/{resume_id} for full field list. "
            "Map these keys to target ATS form field selectors in your automation script."
        ),
    }


# ── Helpers ────────────────────────────────────────────────────────────────

def _first_name(full_name: str | None) -> str | None:
    if not full_name:
        return None
    parts = full_name.strip().split()
    return parts[0] if parts else None


def _last_name(full_name: str | None) -> str | None:
    if not full_name:
        return None
    parts = full_name.strip().split()
    return parts[-1] if len(parts) > 1 else None
