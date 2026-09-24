from datetime import datetime

from pydantic import BaseModel

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

