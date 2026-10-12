from datetime import datetime

from pydantic import BaseModel

class RecommendationResponse(BaseModel):
    recommendation_id: int
    student_id: int
    job_id: int
    job_title: str
    company_name: str
    location: str
    score: float
    reason: str
    matching_method: str
    created_at: datetime
    matched_skills: list[str]
    missing_skills: list[str]

    class Config:
        from_attributes = True
