from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum


class JobStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class JobResponse(BaseModel):
    job_id: int
    company_id: int
    title: str
    description: str
    location: str
    salary: str
    job_type: str
    experience_level: str
    deadline: date
    status: JobStatus
    created_at: datetime
    update_at: datetime

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    company_id: int
    title: str
    description: str
    location: str
    salary: str
    job_type: str
    experience_level: str
    deadline: date
    status: JobStatus

class JobUpdate(BaseModel):
    title: str
    description: str
    location: str
    salary: str
    job_type: str
    experience_level: str
    deadline: date
    status: JobStatus