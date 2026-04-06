import json
import re
from typing import List
from app.core.logger import get_logger
from app.models.schemas import ParsedResume, CoverLetterRequest
from app.models.agent_schemas import (
    CategorizedSkills,
    InternshipListing,
    MatchEvaluation,
    JobApplicationData,
    FinalApplicationPackage,
)
from app.services.llm_service import LLMService
from app.services.matching_service import MatchingService
from app.services.cover_letter_service import CoverLetterService
from app.agents.resume_tailor_agent import ResumeTailorAgent
from app.agents.email_agent import EmailAgent

logger = get_logger(__name__)


def build_search_link(company: str, role: str, location: str) -> str:
    query = " ".join(part for part in [company, role, "internship", "careers", location] if part)
    return f"https://www.google.com/search?q={query.replace(' ', '+')}"

class ApplicationWorkflow:
    """
    Orchestrates the multi-agent pipeline:
    1. Parse Resume (expected to be done prior)
    2. Skill Categorization
    3. Internship Discovery
    4. Job Matching
    5. Cover Letter Generation (with RAG via CoverLetterService)
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        matching_service: MatchingService,
        cover_letter_service: CoverLetterService,
        resume_tailor_agent: ResumeTailorAgent,
        email_agent: EmailAgent,
    ):
        self.llm = llm_service
        self.matcher = matching_service
        self.cover_letter_gen = cover_letter_service
        self.resume_tailor = resume_tailor_agent
        self.email_agent = email_agent

    def run_discovery(self, resume_id: str, parsed_resume: ParsedResume, preferred_field: str, location: str) -> FinalApplicationPackage:
        logger.info(f"Starting Multi-Agent Discovery Workflow for resume_id={resume_id}")
        
        # Agent 2: Skill Categorization
        categorized_skills = self._agent_categorize_skills(parsed_resume.skills)
        
        # Agent 3: Internship Discovery
        internships = self._agent_discover_internships(categorized_skills, preferred_field, location)
        
        applications = []
        for internship in internships:
            # Agent 4: Job Matching
            match_response = self.matcher.match(
                resume_id=resume_id,
                parsed_resume=parsed_resume,
                job_description=internship.description
            )
            
            match_eval = MatchEvaluation(
                match_score=int(match_response.match_score // 10), # scale to 1-10
                reasoning=f"Matched skills: {', '.join(match_response.matched_skills)}. Missing: {', '.join(match_response.missing_skills)}.",
                recommendation=match_response.recommendation
            )
            
            applications.append(JobApplicationData(
                internship=internship,
                match_evaluation=match_eval,
                cover_letter=None,
                tailored_resume=None,
                email_subject=None,
                email_body=None
            ))
            
        # Sort by highest match_score first
        applications.sort(key=lambda x: x.match_evaluation.match_score, reverse=True)
            
        return FinalApplicationPackage(
            resume_id=resume_id,
            categorized_skills=categorized_skills,
            applications=applications
        )

    def run_generation(self, resume_id: str, parsed_resume: ParsedResume, internship: InternshipListing, user_name: str = "The Candidate", user_email: str = "the_candidate@example.com"):
        from app.models.agent_schemas import GeneratedMaterialsResponse
        logger.info(f"Starting Generation Workflow for resume_id={resume_id}, company={internship.company}")
        
        # Agent 5 & 6: RAG Context Retrieval & Cover Letter Generation
        cl_req = CoverLetterRequest(
            resume_id=resume_id,
            job_description=internship.description,
            company_name=internship.company,
            job_title=internship.role,
            tone="professional"
        )
        cl_resp = self.cover_letter_gen.generate(resume_id, parsed_resume, cl_req)
        cover_letter = cl_resp.cover_letter

        # Agent: Resume Tailoring
        tailored_resume = self.resume_tailor.tailor(parsed_resume, internship.description)

        # Prioritize the properly spaced and capitalized name/email extracted from the actual PDF resume! 
        # (Login profiles are often typed quickly without spaces)
        final_name = parsed_resume.name if parsed_resume.name else user_name
        final_email = parsed_resume.email if parsed_resume.email else user_email

        # Agent: Email Generation
        email_draft = self.email_agent.draft_email(internship.role, internship.company, cover_letter, final_name, final_email)
        email_subject = email_draft.get("subject", "")
        email_body = email_draft.get("body", "")
        
        return GeneratedMaterialsResponse(
            cover_letter=cover_letter,
            tailored_resume=tailored_resume,
            email_subject=email_subject,
            email_body=email_body
        )

    def _agent_categorize_skills(self, skills: List[str]) -> CategorizedSkills:
        prompt = f"""
        You are a technical skills classification AI.
        Categorize the following skills into three categories:
        1. Programming Languages
        2. AI/ML Skills
        3. Tools and Frameworks

        Skills: {skills}

        Return strictly valid JSON corresponding to this format:
        {{
            "programming_languages": [],
            "ai_ml_skills": [],
            "tools_frameworks": []
        }}
        """
        response = self.llm.generate(prompt=prompt, temperature=0.0)
        
        # Extract JSON object from potentially chatty response using regex
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            response = match.group(0)
            
        try:
            data = json.loads(response.strip())
            return CategorizedSkills(**data)
        except Exception as e:
            logger.error(f"Failed to parse CategorizedSkills JSON: {e}")
            return CategorizedSkills()

    def _agent_discover_internships(self, skills: CategorizedSkills, preferred_field: str, location: str) -> List[InternshipListing]:
        from app.core.config import settings
        
        # 0th Attempt: Skip immediately if no API key is provided
        if not settings.APIFY_API_KEY or settings.APIFY_API_KEY.strip() == "":
            logger.info("APIFY_API_KEY is missing or empty. Skipping live scraping and using LLM simulation.")
            return self._agent_discover_internships_llm(skills, preferred_field, location)

        query = f"{preferred_field} internship student in {location}"
        logger.info(f"Fetching real internships from Apify for: {query}")
        
        # We try popular Apify Google Jobs Scrapers using the official SDK
        internships = []
        try:
            from apify_client import ApifyClient
            client = ApifyClient(settings.APIFY_API_KEY)
        except ImportError:
            logger.warning("apify_client not installed. Falling back to LLM simulated internships.")
            return self._agent_discover_internships_llm(skills, preferred_field, location)
            
        try:
            # 1st Attempt: epctex google-jobs-scraper
            run_input = {
                "queries": query,
                "maxItems": 15,
                "csvFriendlyOutput": False
            }
            
            logger.info("Calling epctex/google-jobs-scraper actor via ApifyClient...")
            # Use wait_secs or timeout in call() if available, otherwise just use a safety guard.
            # In Apify-Client 1.x, timeout is handled by actor().call(... timeout_secs=60)
            run = client.actor("epctex/google-jobs-scraper").call(run_input=run_input, timeout_secs=60)
            
            if run and run.get("defaultDatasetId"):
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    role = item.get("title", item.get("positionName", "Intern"))
                    company = item.get("companyName", item.get("company", "Unknown"))
                    loc = item.get("location", "Remote")
                    desc = item.get("description", "No description.")
                    link = item.get("jobUrl", item.get("url", ""))
                    
                    if not link and "applyLink" in item:
                        link = item["applyLink"]
                        
                    internships.append(InternshipListing(
                        role=role,
                        company=company,
                        location=loc,
                        description=desc[:2000],
                        application_link=link
                    ))
                    
                # We want maximum 15 internships internally to avoid massive token overhead
                internships = internships[:15]
                
            if internships:
                logger.info(f"Apify successfully scraped {len(internships)} real internships!")
                return internships
        except Exception as e:
            logger.error(f"Apify epctex scraper failed: {e}. Trying hannah66 fallback...")
            
            # 2nd Attempt: hannah66/google-jobs-scraper
            try:
                run_input_fb = {"searchQuery": query, "maxItems": 6}
                logger.info("Calling hannah66/google-jobs-scraper actor via ApifyClient...")
                run_fb = client.actor("hannah66/google-jobs-scraper").call(run_input=run_input_fb, timeout_secs=45)
                
                if run_fb and run_fb.get("defaultDatasetId"):
                    for item in client.dataset(run_fb["defaultDatasetId"]).iterate_items():
                        internships.append(InternshipListing(
                            role=item.get("title", "Intern"),
                            company=item.get("companyName", "Unknown"),
                            location=item.get("location", "Remote"),
                            description=item.get("description", "No description.")[:2000],
                            application_link=item.get("jobUrl", item.get("url", ""))
                        ))
                    
                if internships:
                    logger.info(f"Apify fallback successfully scraped {len(internships)} real internships!")
                    return internships
            except Exception as fallback_e:
                logger.error(f"Fallback Apify scraper failed: {fallback_e}. Using LLM simulation.")
        
        # If all real scraping fails, fallback to LLM generation
        return self._agent_discover_internships_llm(skills, preferred_field, location)

    def _agent_discover_internships_llm(self, skills: CategorizedSkills, preferred_field: str, location: str) -> List[InternshipListing]:
        prompt = f"""
        You are an internship discovery assistant.
        Based on the student's skills and preferences, generate 8 highly relevant simulated internship opportunities.

        Student Skills: {skills.model_dump_json()}
        Preferred Field: {preferred_field}
        Preferred Location: {location}

        Return exactly 8 internships in strictly valid array JSON format:
        [
            {{
                "role": "Role Title",
                "company": "Company Name",
                "location": "Location",
                "description": "Short job description including required skills.",
                "application_link": "https://company-careers-page.example/job-posting"
            }}
        ]
        Use a real company careers/job URL when known. If unknown, return an empty string.
        """
        response = self.llm.generate(prompt=prompt, temperature=0.7)
        
        # Extract JSON array from potentially chatty response using regex
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            response = match.group(0)
            
        try:
            data = json.loads(response.strip())
            internships = []
            for item in data:
                application_link = item.get("application_link", "")
                if not application_link or "example.com" in application_link:
                    application_link = build_search_link(
                        item.get("company", ""),
                        item.get("role", ""),
                        item.get("location", ""),
                    )

                internships.append(InternshipListing(
                    role=item.get("role", "Intern"),
                    company=item.get("company", "Unknown"),
                    location=item.get("location", "Remote"),
                    description=item.get("description", "No description."),
                    application_link=application_link,
                ))

            return internships
        except Exception as e:
            logger.error(f"Failed to parse InternshipListing JSON: {e}")
            return []
