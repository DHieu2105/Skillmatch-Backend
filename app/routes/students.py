from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.cv import CV
from ..models.student_skill import StudentSkill
from ..schemas.student import (
    StudentProfileResponse,
    StudentProfileCreate,
    StudentProfileUpdate,
    ProfileCompletionResponse,
)

router = APIRouter()


def require_student(current_user: User):
    if current_user.role.upper() != "STUDENT":
        raise HTTPException(status_code=403, detail="Student role required")


@router.post("/profile", response_model=StudentProfileResponse, status_code=201)
def create_student_profile(
    profile_data: StudentProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_student(current_user)

    existing_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists",
        )

    now = datetime.utcnow()
    student_profile = StudentProfile(
        user_id=current_user.user_id,
        full_name=profile_data.full_name,
        date_of_birth=profile_data.date_of_birth,
        gender=profile_data.gender,
        university=profile_data.university,
        major=profile_data.major,
        gpa=profile_data.gpa,
        graduation_year=profile_data.graduation_year,
        career_goal=profile_data.career_goal,
        created_at=now,
        update_at=now,
    )
    db.add(student_profile)
    db.commit()
    db.refresh(student_profile)

    return student_profile


@router.get("/profile", response_model=StudentProfileResponse)
def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_student(current_user)

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
    require_student(current_user)

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

    student_profile.update_at = datetime.utcnow()
    db.commit()
    db.refresh(student_profile)

    return student_profile


@router.get("/profile/completion", response_model=ProfileCompletionResponse)
def get_profile_completion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_student(current_user)

    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        return ProfileCompletionResponse(
            percentage=0,
            profile_fields_completed=0,
            profile_fields_total=8,
            has_cv=False,
            has_skills=False,
        )

    profile_values = [
        student_profile.full_name,
        student_profile.date_of_birth,
        student_profile.gender,
        student_profile.university,
        student_profile.major,
        student_profile.gpa,
        student_profile.graduation_year,
        student_profile.career_goal,
    ]
    completed_fields = sum(
        1
        for value in profile_values
        if value is not None
        and (not isinstance(value, str) or value.strip() != "")
    )
    has_cv = db.query(CV).filter(
        CV.student_id == student_profile.student_id
    ).first() is not None
    has_skills = db.query(StudentSkill).filter(
        StudentSkill.student_id == student_profile.student_id
    ).first() is not None

    profile_score = round(completed_fields / len(profile_values) * 60)
    percentage = profile_score
    if has_cv:
        percentage += 20
    if has_skills:
        percentage += 20

    return ProfileCompletionResponse(
        percentage=min(percentage, 100),
        profile_fields_completed=completed_fields,
        profile_fields_total=len(profile_values),
        has_cv=has_cv,
        has_skills=has_skills,
    )