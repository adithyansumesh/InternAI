from app.core.logger import get_logger
from app.services.llm_service import LLMService
from app.models.schemas import ParsedResume

logger = get_logger(__name__)

class ResumeTailorAgent:
    """Agent responsible for tailoring an individual's resume to a specific job description."""
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def tailor(self, parsed_resume: ParsedResume, job_description: str) -> str:
        logger.info("Tailoring resume for specific job description...")
        
        prompt = f"""
        You are an expert technical recruiter and resume writer.
        Your task is to tailor the following resume specifically for the provided job description.
        
        Rules:
        - Highlight the skills from the resume that are most relevant to the job.
        - Emphasize matching projects and experience.
        - Reorder content to put the most relevant information first if needed.
        - DO NOT invent fake information, skills, or experiences. Only use what is provided in the candidate's actual profile.
        - Output the tailored resume in clean, professional Markdown format that is ready to be parsed/downloaded.

        Job Description:
        {job_description}

        Candidate's Profile (Extracted from original resume):
        {parsed_resume.model_dump_json(indent=2)}
        """
        
        response = self.llm.generate(prompt=prompt, temperature=0.5)
        return response.strip()
