from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.job import Job
from ..models.job_skill import JobSkill
from ..models.skill import Skill
from .jobs import require_company_access
from ..schemas.job_skill import JobSkillCreate, JobSkillResponse, JobSkillUpdate

router = APIRouter()

@router.get("/job_skills", response_model=list[JobSkillResponse])
def get_job_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job_skills = db.query(JobSkill).all()
    return job_skills


def get_job_or_404(job_id: int, db: Session):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/skills", response_model=list[JobSkillResponse])
def get_skills_for_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_job_or_404(job_id, db)
    return db.query(JobSkill).filter(JobSkill.job_id == job_id).all()


@router.post("/{job_id}/skills", response_model=JobSkillResponse, status_code=201)
def add_skill_to_job(
    job_id: int,
    skill_data: JobSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(job_id, db)
    require_company_access(current_user, job.company_id, db)

    if not db.query(Skill).filter(Skill.skill_id == skill_data.skill_id).first():
        raise HTTPException(status_code=404, detail="Skill not found")
    if db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_data.skill_id,
    ).first():
        raise HTTPException(status_code=409, detail="Skill is already assigned to this job")

    job_skill = JobSkill(job_id=job_id, **skill_data.model_dump())
    db.add(job_skill)
    db.commit()
    db.refresh(job_skill)
    return job_skill


@router.put("/{job_id}/skills/{skill_id}", response_model=JobSkillResponse)
def update_job_skill(
    job_id: int,
    skill_id: int,
    skill_data: JobSkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(job_id, db)
    require_company_access(current_user, job.company_id, db)

    job_skill = db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id,
    ).first()
    if not job_skill:
        raise HTTPException(status_code=404, detail="Job skill not found")
    if not db.query(Skill).filter(Skill.skill_id == skill_data.skill_id).first():
        raise HTTPException(status_code=404, detail="Skill not found")
    if skill_data.skill_id != skill_id and db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_data.skill_id,
    ).first():
        raise HTTPException(status_code=409, detail="Skill is already assigned to this job")

    job_skill.skill_id = skill_data.skill_id
    job_skill.requirement_type = skill_data.requirement_type
    job_skill.level = skill_data.level
    db.commit()
    db.refresh(job_skill)
    return job_skill


@router.delete("/{job_id}/skills/{skill_id}", response_model=dict)
def remove_skill_from_job(
    job_id: int,
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(job_id, db)
    require_company_access(current_user, job.company_id, db)

    job_skill = db.query(JobSkill).filter(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id,
    ).first()
    if not job_skill:
        raise HTTPException(status_code=404, detail="Job skill not found")

    db.delete(job_skill)
    db.commit()
    return {"message": "Skill removed from job successfully"}

