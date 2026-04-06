from sqlalchemy import Column, Integer, String, JSON, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Store profiles details
    university = Column(String, nullable=True)
    skills = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    achievements = Column(JSON, default=list)

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    description = Column(String)
    required_skills = Column(JSON, default=list)

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    raw_text = Column(Text)
    parsed_json = Column(JSON)  # Stores the full ParsedResume schema
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="resumes")

class SavedInternship(Base):
    __tablename__ = "saved_internships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    internship_id = Column(Integer, ForeignKey("internships.id"))
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
    internship = relationship("Internship")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    internship_id = Column(Integer, ForeignKey("internships.id"))
    resume_id = Column(String, ForeignKey("resumes.id"))
    status = Column(String, default="applied") # applied, interview, rejected, offered
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
    cover_letter = Column(Text, nullable=True)

    user = relationship("User")
    internship = relationship("Internship")
    resume = relationship("Resume")

# Update User model to have relationship
User.resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

