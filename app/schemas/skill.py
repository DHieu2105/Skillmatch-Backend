from pydantic import BaseModel


class SkillBase(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    description: str

    class Config:
        from_attributes = True


class SkillResponse(SkillBase):
    level: str
    source: str


class SkillCreate(BaseModel):
    skill_id: int
    level: str
    source: str