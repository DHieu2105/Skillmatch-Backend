from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.application import Application
from ..models.student_profile import StudentProfile
from ..models.job import Job
from ..models.cv import CV
from ..models.recruiter_profile import RecruiterProfile
from ..schemas.application import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate

router = APIRouter()


@router.post("/applications", response_model=ApplicationResponse)
def create_application(
	application_data: ApplicationCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	student_profile = db.query(StudentProfile).filter(
		StudentProfile.user_id == current_user.user_id
	).first()

	if not student_profile:
		raise HTTPException(status_code=404, detail="Student profile not found")

	job = db.query(Job).filter(
		Job.job_id == application_data.job_id
	).first()

	if not job:
		raise HTTPException(status_code=404, detail="Job not found")

	cv = db.query(CV).filter(
		CV.cv_id == application_data.cv_id,
		CV.student_id == student_profile.student_id,
	).first()

	if not cv:
		raise HTTPException(status_code=404, detail="CV not found")

	if job.status.upper() != "OPEN":
		raise HTTPException(status_code=400, detail="Job is not open")

	existing_application = db.query(Application).filter(
		Application.student_id == student_profile.student_id,
		Application.job_id == application_data.job_id,
	).first()

	if existing_application:
		raise HTTPException(
			status_code=400,
			detail="You have already applied for this job",
		)

	now = datetime.utcnow()
	application = Application(
		student_id=student_profile.student_id,
		job_id=application_data.job_id,
		cv_id=application_data.cv_id,
		cover_letter=application_data.cover_letter,
		status="APPLIED",
		applied_at=now,
		updated_at=now,
	)

	db.add(application)
	db.commit()
	db.refresh(application)

	return application


@router.get("/jobs/{job_id}/applications", response_model=list[ApplicationResponse])
def get_job_applications(
	job_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	if current_user.role.upper() != "RECRUITER":
		raise HTTPException(status_code=403, detail="Recruiter role required")

	recruiter_profile = db.query(RecruiterProfile).filter(
		RecruiterProfile.user_id == current_user.user_id
	).first()

	if not recruiter_profile:
		raise HTTPException(status_code=404, detail="Recruiter profile not found")

	job = db.query(Job).filter(
		Job.job_id == job_id
	).first()

	if not job:
		raise HTTPException(status_code=404, detail="Job not found")

	if job.company_id != recruiter_profile.company_id:
		raise HTTPException(
			status_code=403,
			detail="You do not have permission to view this job's applications",
		)

	applications = db.query(Application).filter(
		Application.job_id == job_id
	).all()

	return applications

@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.upper() != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Recruiter role required"
        )

    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id
    ).first()

    if not recruiter_profile:
        raise HTTPException(
            status_code=404,
            detail="Recruiter profile not found"
        )

    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    job = db.query(Job).filter(
        Job.job_id == application.job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.company_id != recruiter_profile.company_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update this application"
        )

    allowed_statuses = {
        "APPLIED",
        "REVIEWING",
        "INTERVIEW",
        "ACCEPTED",
        "REJECTED",
    }

    if status_data.status.upper() not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid application status"
        )

    application.status = status_data.status.upper()
    application.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(application)

    return application