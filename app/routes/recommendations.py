from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.nlp.matcher import calculate_similarity
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.cv import CV
from ..models.job import Job
from ..schemas.recommendation import RecommendationResponse

router = APIRouter(prefix="/recommendations")

@router.get("", response_model=list[RecommendationResponse])
def get_my_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    recommendations = db.query(Recommendation).filter(
        Recommendation.student_id == student_profile.student_id
    ).all()

    return recommendations


@router.post(
    "/generate",
    response_model=list[RecommendationResponse]
)
def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    cv = db.query(CV).filter(
        CV.student_id == student_profile.student_id,
        CV.is_default == True
    ).first()

    if not cv:
        raise HTTPException(
            status_code=404,
            detail="Default CV not found"
        )

    jobs = db.query(Job).filter(Job.status == "OPEN").all()

    for job in jobs:
        score = calculate_similarity(
            cv.parsed_text,
            job.description
        ) * 100

        recommendation = db.query(Recommendation).filter(
            Recommendation.student_id == student_profile.student_id,
            Recommendation.job_id == job.job_id
        ).first()

        if recommendation:
            recommendation.score = score
            recommendation.reason = (
                "Based on CV and job description similarity"
            )
            recommendation.matching_method = "TF_IDF"
        else:
            recommendation = Recommendation(
                student_id=student_profile.student_id,
                job_id=job.job_id,
                score=score,
                reason="Based on CV and job description similarity",
                matching_method="TF_IDF",
                created_at=datetime.utcnow()
            )
            db.add(recommendation)

    db.commit()

    recommendations = db.query(Recommendation).filter(
        Recommendation.student_id == student_profile.student_id
    ).order_by(
        Recommendation.score.desc()
    ).all()

    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_my_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id,
        Recommendation.student_id == student_profile.student_id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    return recommendation