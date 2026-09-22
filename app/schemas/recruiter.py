from pydantic import BaseModel

class RecruiterProfileResponse(BaseModel):
    recruiter_id: int
    user_id: int
    full_name: str
    phone: str
    position: str
    company_id: int

    class Config:
        from_attributes = True

class RecruiterProfileUpdate(BaseModel):
    full_name: str
    phone: str
    position: str
    company_id: int