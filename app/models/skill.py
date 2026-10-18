# app/models/skill.py
from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Skill(Base):
    __tablename__ = "skills"

    skill_id: Mapped[int] = mapped_column(primary_key=True)
    skill_name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        Index("uq_skill_name_ci", func.lower(skill_name), unique=True),
    )
