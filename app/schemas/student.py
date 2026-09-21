from pydantic import BaseModel, Field
from datetime import datetime

class StudentProfileResponse(BaseModel):
    student_id: int
    user_id: int
    full_name: str
    date_of_birth: str
    gender: str
    university: str
    major: str
    gpa: float
    graduation_year: int
    career_goal: str

    class Config:
        from_attributes = True


class StudentProfileUpdate(BaseModel):
    full_name: str
    date_of_birth: str
    gender: str
    university: str
    major: str
    gpa: float
    graduation_year: int
    career_goal: str