# app/models/cv.py
from datetime import datetime
from sqlalchemy import Index, String, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class CV(Base):
    __tablename__ = "cvs"
    __table_args__ = (
        Index(
            "uq_cv_default_per_student",
            "student_id",
            unique=True,
            postgresql_where=text("is_default = true"),
            sqlite_where=text("is_default = 1"),
        ),
    )

    cv_id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.student_id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    parsed_text: Mapped[str] = mapped_column(String, nullable=False)
    is_default: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
