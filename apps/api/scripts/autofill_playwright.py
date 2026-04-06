"""
scripts/autofill_playwright.py — Phase 5: Browser Automation Scaffold.
Demonstrates how to fetch the autofill profile from the backend API
and use Playwright to auto-fill job application forms.

USAGE:
  1. Install: pip install playwright && playwright install chromium
  2. Ensure backend is running: uvicorn app.main:app --reload
  3. Run: python scripts/autofill_playwright.py <resume_id> <job_url>

NOTE: This is a scaffold/demonstration. Selector mappings must be
customized per target ATS platform.
"""

import asyncio
import sys
import httpx

# ── ATS Form Field Selectors ──────────────────────────────────────────────
# Map autofill_fields keys → CSS selectors per platform
# Extend this dict for each platform you want to support.

PLATFORM_SELECTORS = {
    "greenhouse": {
        "first_name": "#first_name",
        "last_name": "#last_name",
        "email": "#email",
        "phone": "#phone",
        "school": "#education_school_name",
        "degree": "#education_degree",
        "current_title": "#job_title",
        "current_company": "#company",
    },
    "lever": {
        "first_name": "input[name='name']",   # Lever uses full name
        "email": "input[name='email']",
        "phone": "input[name='phone']",
        "current_company": "input[name='org']",
    },
    "linkedin_easy_apply": {
        "first_name": "input[id*='firstName']",
        "last_name": "input[id*='lastName']",
        "email": "input[id*='email']",
        "phone": "input[id*='phoneNumber']",
    },
    "generic": {
        "first_name": "input[name*='first'], input[id*='first'], input[placeholder*='First']",
        "last_name": "input[name*='last'], input[id*='last'], input[placeholder*='Last']",
        "email": "input[type='email'], input[name*='email']",
        "phone": "input[type='tel'], input[name*='phone']",
    },
}


async def fetch_autofill_profile(resume_id: str, api_base: str = "http://localhost:8000") -> dict:
    """Fetch the autofill profile from the backend API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{api_base}/api/v1/profile/{resume_id}")
        resp.raise_for_status()
        return resp.json()


async def autofill_application(
    resume_id: str,
    job_url: str,
    platform: str = "generic",
    api_base: str = "http://localhost:8000",
    headless: bool = False,
):
    """
    Main autofill automation function.
    
    Args:
        resume_id: The resume ID from the backend.
        job_url: URL of the job application form.
        platform: Target ATS platform key (see PLATFORM_SELECTORS).
        api_base: Backend API base URL.
        headless: Run browser in headless mode.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        return

    # Fetch profile from API
    print(f"📡 Fetching autofill profile for resume '{resume_id}'...")
    try:
        profile = await fetch_autofill_profile(resume_id, api_base)
    except Exception as e:
        print(f"❌ Failed to fetch profile: {e}")
        return

    fields = profile.get("autofill_fields", {})
    selectors = PLATFORM_SELECTORS.get(platform, PLATFORM_SELECTORS["generic"])

    print(f"✅ Profile loaded: {fields.get('full_name')} | {fields.get('email')}")
    print(f"🌐 Opening: {job_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(job_url, wait_until="networkidle")

        filled_count = 0
        for field_key, selector in selectors.items():
            value = fields.get(field_key)
            if not value:
                continue
            try:
                element = page.locator(selector).first
                if await element.is_visible():
                    await element.fill(str(value))
                    filled_count += 1
                    print(f"  ✏️  Filled '{field_key}': {value[:40]}")
            except Exception as e:
                print(f"  ⚠️  Could not fill '{field_key}' ({selector}): {e}")

        print(f"\n✅ Autofill complete: {filled_count} fields filled")
        print("⏸️  Browser paused. Review and submit manually.")

        # Keep browser open for manual review
        await page.wait_for_timeout(30000)
        await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/autofill_playwright.py <resume_id> <job_url> [platform]")
        print("       platform: greenhouse | lever | linkedin_easy_apply | generic (default)")
        sys.exit(1)

    resume_id = sys.argv[1]
    job_url = sys.argv[2]
    platform = sys.argv[3] if len(sys.argv) > 3 else "generic"

    asyncio.run(autofill_application(resume_id, job_url, platform))
