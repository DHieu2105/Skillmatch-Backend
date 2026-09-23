from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.job import Job
from ..models.recruiter_profile import RecruiterProfile
from ..schemas.job import JobResponse, JobCreate, JobUpdate

router = APIRouter()


def require_recruiter(current_user: User):
    if current_user.role.upper() != "RECRUITER":
        raise HTTPException(status_code=403, detail="Recruiter role required")


def require_company_access(current_user: User, company_id: int, db: Session):
    require_recruiter(current_user)

    recruiter_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.user_id,
        RecruiterProfile.company_id == company_id,
    ).first()
    if not recruiter_profile:
        raise HTTPException(status_code=403, detail="You do not have access to this company")


@router.get("/jobs", response_model=list[JobResponse])
def get_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(    
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

@router.post("/jobs", response_model=JobResponse)
def create_job( 
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_company_access(current_user, job_data.company_id, db)

    new_job = Job(
        company_id=job_data.company_id,
        title=job_data.title,
        description=job_data.description,
        location=job_data.location,
        salary=job_data.salary,
        job_type=job_data.job_type,
        experience_level=job_data.experience_level,
        deadline=job_data.deadline,
        status=job_data.status,
        created_at=datetime.utcnow(),
        update_at=datetime.utcnow()
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    require_company_access(current_user, job.company_id, db)

    job.title = job_data.title
    job.description = job_data.description
    job.location = job_data.location
    job.salary = job_data.salary
    job.job_type = job_data.job_type
    job.experience_level = job_data.experience_level
    job.deadline = job_data.deadline
    job.status = job_data.status
    job.update_at = datetime.utcnow()

    db.commit()
    db.refresh(job)

    return job

@router.delete("/jobs/{job_id}", response_model=dict)
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    require_company_access(current_user, job.company_id, db)

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}

@router.get("/jobs/search", response_model=list[JobResponse])
def search_jobs(   
    title: str = None,
    location: str = None,
    job_type: str = None,
    experience_level: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Job)

    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)

    jobs = query.all()
    return jobs

@router.patch("/jobs/{job_id}/status", response_model=JobResponse)
def update_job_status(
    job_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    require_company_access(current_user, job.company_id, db)

    job.status = status
    job.update_at = datetime.utcnow()

    db.commit()
    db.refresh(job)

    return job