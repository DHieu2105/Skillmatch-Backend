from pydantic import BaseModel, Field
from datetime import date, datetime

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
    status: str
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
    status: str

class JobUpdate(BaseModel):
    title: str
    description: str
    location: str
    salary: str
    job_type: str
    experience_level: str
    deadline: date
    status: str