from pydantic import BaseModel, Field, field_validator


class SkillBase(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    description: str

    class Config:
        from_attributes = True


class SkillCatalogCreate(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)

    @field_validator("skill_name", "category")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Value cannot be empty")
        return normalized


class SkillResponse(SkillBase):
    level: str
    source: str


class SkillCreate(BaseModel):
    skill_id: int
    level: str
    source: str


class SkillUpdate(BaseModel):
    level: str
    source: str
