from pydantic import BaseModel, Field
from datetime import datetime

class ApplicationCreate(BaseModel):
    job_id: int
    cv_id: int
    cover_letter: str
class ApplicationResponse(BaseModel):
    application_id: int
    student_id: int
    job_id: int
    cv_id: int
    cover_letter: str | None
    status: str
    applied_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApplicationStatusUpdate(BaseModel):
    status: str