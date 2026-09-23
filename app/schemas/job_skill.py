from pydantic import BaseModel

class JobSkillResponse(BaseModel):
    job_id: int
    skill_id: int
    requirement_type: str
    level: str

    class Config:
        from_attributes = True

class JobSkillCreate(BaseModel):
    skill_id: int
    requirement_type: str
    level: str

class JobSkillUpdate(BaseModel):
    skill_id: int   
    requirement_type: str
    level: str