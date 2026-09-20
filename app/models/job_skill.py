# app/models/job_skill.py
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = {'extend_existing': True}

    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.job_id"), primary_key=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.skill_id"), primary_key=True, nullable=False)
    requirement_type: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[str] = mapped_column(String, nullable=False)