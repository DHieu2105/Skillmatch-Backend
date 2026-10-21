from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.nlp.matcher import calculate_similarity
from app.nlp.skill_matcher import (
    get_job_skills,
    get_student_skills,
    match_skills,
    calculate_final_score,
)
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.cv import CV
from ..models.job import Job
from ..models.company import Company
from ..models.skill import Skill
from ..schemas.recommendation import RecommendationResponse

router = APIRouter(prefix="/recommendations")


def require_student(current_user: User):
    if current_user.role.upper() != "STUDENT":
        raise HTTPException(status_code=403, detail="Student role required")


def _recommendation_response(
    recommendation: Recommendation,
    db: Session,
) -> RecommendationResponse:
    student_skills = get_student_skills(db, recommendation.student_id)
    job_skills = get_job_skills(db, recommendation.job_id)
    skill_result = match_skills(student_skills, job_skills)
    skill_ids = (
        skill_result["matched_skill_ids"] + skill_result["missing_skill_ids"]
    )
    skills = db.query(Skill).filter(Skill.skill_id.in_(skill_ids)).all()
    skill_names = {skill.skill_id: skill.skill_name for skill in skills}
    job = db.query(Job).filter(
        Job.job_id == recommendation.job_id
    ).first()
    company = None
    if job:
        company = db.query(Company).filter(
            Company.company_id == job.company_id
        ).first()

    cv = db.query(CV).filter(
        CV.student_id == recommendation.student_id,
        CV.is_default == True,
        CV.is_archived == False,
    ).first()
    tfidf_score = (
        calculate_similarity(cv.parsed_text, job.description) * 100
        if cv and job
        else 0.0
    )
    current_score = calculate_final_score(
        tfidf_score,
        skill_result["match_score"],
    )
    matched_count = len(skill_result["matched_skill_ids"])
    missing_count = len(skill_result["missing_skill_ids"])
    reason = (
        f"Matched {matched_count}/{len(job_skills)} job skills"
        f", missing or below level for {missing_count} skills"
    )

    return RecommendationResponse(
        recommendation_id=recommendation.recommendation_id,
        student_id=recommendation.student_id,
        job_id=recommendation.job_id,
        job_title=job.title if job else "Unknown Job",
        company_name=company.company_name if company else "Unknown Company",
        location=job.location if job else "",
        score=current_score,
        reason=reason,
        matching_method=recommendation.matching_method,
        created_at=recommendation.created_at,
        matched_skills=[
            skill_names[skill_id]
            for skill_id in skill_result["matched_skill_ids"]
        ],
        missing_skills=[
            skill_names[skill_id]
            for skill_id in skill_result["missing_skill_ids"]
        ],
    )

@router.get("", response_model=list[RecommendationResponse])
def get_my_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    recommendations = db.query(Recommendation).filter(
        Recommendation.student_id == student_profile.student_id
    ).order_by(
        Recommendation.score.desc()
    ).all()

    responses = [
        _recommendation_response(recommendation, db)
        for recommendation in recommendations
    ]
    return sorted(responses, key=lambda item: item.score, reverse=True)


@router.post(
    "/generate",
    response_model=list[RecommendationResponse]
)
def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    cv = db.query(CV).filter(
        CV.student_id == student_profile.student_id,
        CV.is_default == True,
        CV.is_archived == False,
    ).first()

    if not cv:
        raise HTTPException(
            status_code=404,
            detail="Default CV not found"
        )

    jobs = db.query(Job).filter(
        Job.status == "OPEN",
        Job.deadline >= date.today(),
    ).all()
    open_job_ids = {job.job_id for job in jobs}
    stale_recommendations = db.query(Recommendation).filter(
        Recommendation.student_id == student_profile.student_id,
    )
    if open_job_ids:
        stale_recommendations = stale_recommendations.filter(
            ~Recommendation.job_id.in_(open_job_ids)
        )

    for recommendation in stale_recommendations.all():
        db.delete(recommendation)

    student_skills = get_student_skills(db, student_profile.student_id)

    for job in jobs:
        score = calculate_similarity(
            cv.parsed_text,
            job.description
        ) * 100

        job_skills = get_job_skills(db, job.job_id)

        skill_result = match_skills(
            student_skills,
            job_skills,
        )
        matched_count = len(skill_result["matched_skill_ids"])
        missing_count = len(skill_result["missing_skill_ids"])
        total_count = len(job_skills)

        reason = (
            f"Matched {matched_count}/{total_count} job skills"
            f", missing or below level for {missing_count} skills"
        )

        score = calculate_final_score(
            score,
            skill_result["match_score"]
        )

        existing_recommendation = db.query(Recommendation).filter(
            Recommendation.student_id == student_profile.student_id,
            Recommendation.job_id == job.job_id
        ).first()

        if existing_recommendation:
            existing_recommendation.score = score
            existing_recommendation.reason = reason
            existing_recommendation.matching_method = "TF_IDF + SKILL_MATCHING"
            existing_recommendation.created_at = datetime.utcnow()
        else:
            recommendation = Recommendation(
                student_id=student_profile.student_id,
                job_id=job.job_id,
                score=score,
                reason=reason,
                matching_method="TF_IDF + SKILL_MATCHING",
                created_at=datetime.utcnow()
            )
            db.add(recommendation)

    db.commit()

    recommendations = db.query(Recommendation).filter(
        Recommendation.student_id == student_profile.student_id
    ).order_by(
        Recommendation.score.desc()
    ).all()

    return [
        _recommendation_response(recommendation, db)
        for recommendation in recommendations
    ]


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_my_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    recommendation = db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id,
        Recommendation.student_id == student_profile.student_id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    return _recommendation_response(recommendation, db)
