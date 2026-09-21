from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..schemas.student import StudentProfileResponse, StudentProfileUpdate

router = APIRouter()

@router.get("/profile", response_model=StudentProfileResponse)
def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return student_profile

@router.put("/profile", response_model=StudentProfileResponse)
def update_student_profile(
    profile_data: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    student_profile.full_name = profile_data.full_name
    student_profile.date_of_birth = profile_data.date_of_birth
    student_profile.gender = profile_data.gender
    student_profile.university = profile_data.university
    student_profile.major = profile_data.major
    student_profile.gpa = profile_data.gpa
    student_profile.graduation_year = profile_data.graduation_year
    student_profile.career_goal = profile_data.career_goal

    db.commit()
    db.refresh(student_profile)

    return student_profile