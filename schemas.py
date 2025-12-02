from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# Company schemas
class CompanyRequest(BaseModel):
    company_name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class CompanyResponse(BaseModel):
    company_id: UUID
    success: bool
    message: str


# Job Posting schemas
class JobPostingRequest(BaseModel):
    company_id: UUID
    job_title: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[int] = None
    pay_period: Optional[str] = None  # hourly, monthly, yearly
    work_type: Optional[str] = None  # Fulltime, Parttime, Contract, Season
    experience_level: Optional[str] = None  # Intern, Fresher, Junior, Senior, Executive
    location: Optional[str] = None
    applies: Optional[int] = None
    listed_time: Optional[datetime] = None
    currency: Optional[str] = None
    platform: Optional[str] = None
    url: Optional[str] = None


class JobPostingResponse(BaseModel):
    job_id: UUID
    success: bool
    message: str
    crawled_time: datetime


# Benefit schemas
class BenefitRequest(BaseModel):
    job_id: UUID
    type: Optional[str] = None
    inferred: Optional[str] = None


class BenefitResponse(BaseModel):
    benefit_id: int
    success: bool
    message: str


# Check URL schema
class URLCheckRequest(BaseModel):
    url: str


class URLCheckResponse(BaseModel):
    url: str
    is_crawled: bool
    job_id: Optional[UUID] = None
    crawled_time: Optional[datetime] = None


# Delete schemas
class DeleteResponse(BaseModel):
    success: bool
    message: str
