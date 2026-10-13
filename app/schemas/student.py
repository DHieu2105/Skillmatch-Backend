from pydantic import BaseModel, Field

class StudentProfileResponse(BaseModel):
    student_id: int
    user_id: int
    full_name: str
    date_of_birth: str
    gender: str
    university: str
    major: str
    gpa: float = Field(..., ge=0, le=4)
    graduation_year: int = Field(..., ge=1900, le=2100)
    career_goal: str

    class Config:
        from_attributes = True


class StudentProfileCreate(BaseModel):
    full_name: str
    date_of_birth: str
    gender: str
    university: str
    major: str
    gpa: float = Field(..., ge=0, le=4)
    graduation_year: int = Field(..., ge=1900, le=2100)
    career_goal: str


class StudentProfileUpdate(StudentProfileCreate):
    pass


class ProfileCompletionResponse(BaseModel):
    percentage: int
    profile_fields_completed: int
    profile_fields_total: int
    has_cv: bool
    has_skills: bool