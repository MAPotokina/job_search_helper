from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base


class Job(Base):
    """Job model"""
    __tablename__ = "jobs"
    
    # Main fields
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    job_url = Column(String(500))
    job_description = Column(Text)
    
    # LLM analysis fields
    has_visa_sponsorship = Column(Boolean, nullable=True)
    sponsorship_analysis = Column(Text, nullable=True)
    resume_match_percentage = Column(Integer, nullable=True)
    match_analysis = Column(Text, nullable=True)
    
    # Status and workflow
    status = Column(String(50), default="new")
    cover_letter = Column(Text, nullable=True)
    
    # Dates
    applied_date = Column(DateTime, nullable=True)
    response_date = Column(DateTime, nullable=True)
    days_to_response = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class LLMLog(Base):
    """Model for logging LLM calls"""
    __tablename__ = "llm_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    function_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    execution_time = Column(Float)
    tokens_used = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

