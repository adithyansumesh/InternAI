import requests
from bs4 import BeautifulSoup
from app.models.domain import Internship
import logging

logger = logging.getLogger(__name__)

def fetch_internshala_internships(db, limit=10):
    url = "https://internshala.com/internships/software-development-internships/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        job_cards = soup.find_all("div", class_="container-fluid")
        
        added_count = 0
        for card in job_cards:
            if added_count >= limit:
                break
                
            title_elem = card.find("h3", class_="job-internship-name")
            company_elem = card.find("p", class_="company-name")
            
            if title_elem and company_elem:
                title = title_elem.text.strip()
                company = company_elem.text.strip()
                
                # Check if it already exists to avoid duplicates
                existing = db.query(Internship).filter(
                    Internship.title == title,
                    Internship.company == company
                ).first()
                
                if not existing:
                    # Provide realistic defaults for MVP since description is on details page
                    desc = f"Join {company} as a {title}. Work with the team to develop scalable solutions and contribute to active projects."
                    skills = ["Python", "Algorithms", "Git", "Problem Solving"]
                    
                    # Basic keyword analysis for Skills mapping
                    title_lower = title.lower()
                    if "frontend" in title_lower or "react" in title_lower or "ui" in title_lower:
                        skills = ["React", "HTML/CSS", "JavaScript", "Tailwind"]
                    elif "backend" in title_lower or "node" in title_lower or "django" in title_lower:
                        skills = ["Node.js", "Python", "SQL", "REST APIs"]
                    elif "data" in title_lower or "machine learning" in title_lower:
                        skills = ["Python", "SQL", "Machine Learning", "Pandas"]
                    elif "full stack" in title_lower:
                        skills = ["React", "Node.js", "MongoDB", "Express"]
                        
                    internship = Internship(
                        title=title,
                        company=company,
                        description=desc,
                        required_skills=skills
                    )
                    db.add(internship)
                    added_count += 1
                    
        db.commit()
        return {"status": "success", "added": added_count, "source": "Internshala"}
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return {"status": "error", "message": str(e)}
