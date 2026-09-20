# app/models/student_skill.py
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class StudentSkill(Base):
    __tablename__ = "student_skills"
    __table_args__ = {'extend_existing': True}

    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.student_id"), primary_key=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.skill_id"), primary_key=True, nullable=False)
    level: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)