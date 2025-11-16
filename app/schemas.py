from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobCreate(BaseModel):
    """Схема для создания вакансии"""
    title: str
    company: str
    job_url: Optional[str] = None
    job_description: Optional[str] = None
    status: str = "new"


class JobUpdate(BaseModel):
    """Схема для обновления вакансии (все поля опциональные)"""
    title: Optional[str] = None
    company: Optional[str] = None
    job_url: Optional[str] = None
    job_description: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[datetime] = None
    response_date: Optional[datetime] = None


class JobResponse(BaseModel):
    """Схема ответа с полной информацией о вакансии"""
    id: int
    title: str
    company: str
    job_url: Optional[str]
    job_description: Optional[str]
    has_visa_sponsorship: Optional[bool]
    sponsorship_analysis: Optional[str]
    resume_match_percentage: Optional[int]
    match_analysis: Optional[str]
    status: str
    cover_letter: Optional[str]
    applied_date: Optional[datetime]
    response_date: Optional[datetime]
    days_to_response: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

