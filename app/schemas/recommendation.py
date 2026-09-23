from pydantic import BaseModel, Field
from datetime import datetime

class RecommendationResponse(BaseModel):
    recommendation_id: int
    student_id: int
    job_id: int
    score: float
    reason: str
    matching_method: str
    created_at: datetime

    class Config:
        from_attributes = True

class RecommendationCreate(BaseModel):
    student_id: int
    job_id: int
    score: float
    reason: str
    matching_method: str

class RecommendationUpdate(BaseModel):
    score: float | None = None
    reason: str | None = None
    matching_method: str | None = None 