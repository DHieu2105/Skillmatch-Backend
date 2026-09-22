from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.recruiter_profile import RecruiterProfile
from ..schemas.recruiter import RecruiterProfileResponse, RecruiterProfileUpdate

router = APIRouter()

def require_recruiter(current_user: User):
    if current_user.role.upper() != "RECRUITER":
        raise HTTPException(status_code=403, detail="Recruiter role required")

@router.get("/profile", response_model=RecruiterProfileResponse)
def get_recruiter_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_recruiter(current_user)

    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id
    ).first()

    if not recruiter_profile:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")

    return recruiter_profile

@router.put("/profile", response_model=RecruiterProfileResponse)
def update_recruiter_profile(
    profile_data: RecruiterProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_recruiter(current_user)

    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id
    ).first()

    if not recruiter_profile:
        recruiter_profile = RecruiterProfile(
            user_id=current_user.user_id,
            full_name=profile_data.full_name,
            phone=profile_data.phone,
            position=profile_data.position,
            company_id=profile_data.company_id,
            created_at=datetime.utcnow(),
            update_at=datetime.utcnow(),
        )
        db.add(recruiter_profile)
    else:
        recruiter_profile.full_name = profile_data.full_name
        recruiter_profile.phone = profile_data.phone
        recruiter_profile.position = profile_data.position
        recruiter_profile.company_id = profile_data.company_id
        recruiter_profile.update_at = datetime.utcnow()

    db.commit()
    db.refresh(recruiter_profile)

    return recruiter_profile

