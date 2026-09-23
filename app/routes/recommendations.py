from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.application import Application
from ..models.student_profile import StudentProfile
from ..models.job import Job
from ..models.cv import CV
from ..models.recruiter_profile import RecruiterProfile
from ..schemas.recommendation import RecommendationCreate, RecommendationUpdate, RecommendationResponse

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
def create_recommendation(
    recommendation_data: RecommendationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id
    ).first()

    if not recruiter_profile:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")

    student_profile = db.query(StudentProfile).filter(
        StudentProfile.student_id == recommendation_data.student_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    job = db.query(Job).filter(
        Job.job_id == recommendation_data.job_id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    now = datetime.utcnow()

    new_recommendation = Recommendation(
        student_id=recommendation_data.student_id,
        job_id=recommendation_data.job_id,
        score=recommendation_data.score,
        reason=recommendation_data.reason,
        matching_method=recommendation_data.matching_method,
        created_at=now
    )

    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)

    return new_recommendation

@router.put("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_data: RecommendationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id
    ).first()

    if not recruiter_profile:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")

    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if recommendation_data.score is not None:
        recommendation.score = recommendation_data.score
    if recommendation_data.reason is not None:
        recommendation.reason = recommendation_data.reason
    if recommendation_data.matching_method is not None:
        recommendation.matching_method = recommendation_data.matching_method

    db.commit()
    db.refresh(recommendation)

    return recommendation

@router.get("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id
    ).first()

    if not recruiter_profile:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")

    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return recommendation

@router.get("/recommendations", response_model=list[RecommendationResponse])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id
    ).first()

    if not recruiter_profile:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")

    recommendations = db.query(Recommendation).all()

    return recommendations