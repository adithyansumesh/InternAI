import json
import re
from app.core.logger import get_logger
from app.services.llm_service import LLMService

logger = get_logger(__name__)

class EmailAgent:
    """Agent responsible for drafting professional application emails."""
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def draft_email(self, role: str, company: str, cover_letter: str, user_name: str = "The Candidate", user_email: str = "example@example.com") -> dict:
        logger.info(f"Drafting email for {role} at {company} for {user_name}...")
        
        prompt = f"""
        You are an expert career advisor and technical recruiter.
        Your task is to draft a SHORT, professional application email for an internship.
        The cover letter will be attached as a separate document, so the email body should NOT repeat the entire cover letter.
        Instead, it should be a brief, high-impact outreach.

        === PROFESSIONAL OUTREACH TEMPLATE ===
        Subject: Application for {role} at {company}

        Dear [Hiring Manager's Name or Hiring Team],

        I am writing to express my strong interest in the {role} position at {company}, as I am a [Candidate's Degree/Year] student with a focus on [Candidate's Main Field].

        I have attached my tailored resume and cover letter, which provide more detail on my background in [mention 1-2 key skills or projects]. I would welcome the opportunity to discuss how my skills and enthusiasm could contribute to the {company} team.

        Thank you for your time and consideration.

        Best regards,
        {user_name}
        {user_email}

        === INPUT DATA ===
        Role: {role}
        Company: {company}
        Candidate Info: {user_name}, {user_email}
        Detailed Cover Letter context (use only to customize the template above): {cover_letter[:1000]}

        === RULES ===
        1. YOU MUST NOT include any conversational text before or after the JSON.
        2. YOU MUST use the "PROFESSIONAL OUTREACH TEMPLATE" structure.
        3. Keep the body brief (under 150 words).
        4. Focus on being a professional introduction to the attached materials.
        5. Return ONLY the JSON object.

        Output Format (STRICT JSON ONLY):
        {{
            "subject": "Application for {role} at {company}",
            "body": "Dear [Name],\\n\\nI am writing to...\\n\\nBest regards,\\n{user_name}\\n{user_email}"
        }}
        """
        
        response = self.llm.generate(prompt=prompt, temperature=0.5).strip()
        
        # Improved JSON extraction and cleaning
        # Handle cases where LLM might include markdown or extra text
        json_content = response
        if "```json" in response:
            json_content = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_content = response.split("```")[1].split("```")[0]
        
        # Clean up common JSON parsing issues from certain LLMs
        json_content = json_content.replace("\\n", "\n") # Unescape newlines if LLM escaped them
        # Re-escape only what's necessary for json.loads or use a more robust approach
        
        # Better: find the actual JSON block using regex more robustly
        json_match = re.search(r'(\{.*\}|\[.*\])', json_content, re.DOTALL)
        if json_match:
            json_content = json_match.group(0)
            
        try:
            # First try a standard load
            parsed = json.loads(json_content.strip())
            if "subject" in parsed and "body" in parsed:
                return {
                    "subject": str(parsed["subject"]).strip(),
                    "body": str(parsed["body"]).strip()
                }
            raise ValueError("Missing keys")
            
        except Exception as e:
            logger.warning(f"Standard JSON parsing failed: {e}. Attempting surgical recovery...")
            
            # Surgical extraction for "subject"
            subject_match = re.search(r'"subject":\s*"(.*?)"', json_content, re.DOTALL)
            subject = subject_match.group(1).strip() if subject_match else f"Application for {role} at {company}"
            
            # Surgical extraction for "body"
            body_match = re.search(r'"body":\s*"(.*?)"', json_content, re.DOTALL)
            if body_match:
                body = body_match.group(1)
                # If we got a raw string with unescaped newlines, this regex with DOTALL will catch it
                # We should unescape any literal \n back to actual newlines for the final output
                body = body.replace("\\n", "\n").replace("\\t", "\t").strip()
                return {"subject": subject, "body": body}
            
            # Ultimate fallback if we can find ANY structure
            logger.error(f"Surgical parsing failed. Using raw response as body.")
            return {
                "subject": f"Application for {role} at {company}",
                "body": response.strip().replace("```json", "").replace("```", "").strip()
            }
