from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.skill import Skill
from ..models.student_skill import StudentSkill
from ..services.skill_catalog import sync_skill_id_sequence
from ..schemas.skill import (
    SkillBase,
    SkillCatalogCreate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
)

router = APIRouter()


def require_student(current_user: User):
    if current_user.role.upper() != "STUDENT":
        raise HTTPException(status_code=403, detail="Student role required")


@router.get("/catalog", response_model=list[SkillBase])
def get_skill_catalog(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Skill).order_by(Skill.skill_name.asc()).all()


@router.post("/catalog", response_model=SkillBase, status_code=status.HTTP_201_CREATED)
def create_catalog_skill(
    skill_data: SkillCatalogCreate,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.upper() not in {"STUDENT", "RECRUITER"}:
        raise HTTPException(status_code=403, detail="User role not allowed")

    normalized_name = skill_data.skill_name.casefold()
    if db.bind and db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:skill_name))"),
            {"skill_name": normalized_name},
        )

    existing_skill = db.query(Skill).filter(
        func.lower(Skill.skill_name) == normalized_name
    ).first()

    if existing_skill:
        response.status_code = status.HTTP_200_OK
        return existing_skill

    sync_skill_id_sequence(db)
    skill = Skill(
        skill_name=skill_data.skill_name,
        category=skill_data.category,
        description=f"{skill_data.skill_name} skill in {skill_data.category}.",
    )
    db.add(skill)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing_skill = db.query(Skill).filter(
            func.lower(Skill.skill_name) == normalized_name
        ).first()
        if existing_skill:
            response.status_code = status.HTTP_200_OK
            return existing_skill
        raise

    db.refresh(skill)
    return skill


@router.get("", response_model=list[SkillResponse])
def get_student_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_student(current_user)

    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    student_skills = db.query(StudentSkill).filter(
        StudentSkill.student_id == student_profile.student_id
    ).all()

    skills = []
    for student_skill in student_skills:
        skill = db.query(Skill).filter(Skill.skill_id == student_skill.skill_id).first()
        if skill:
            skills.append(
                SkillResponse(
                    skill_id=skill.skill_id,
                    skill_name=skill.skill_name,
                    category=skill.category,
                    description=skill.description,
                    level=student_skill.level,
                    source=student_skill.source,
                )
            )

    return skills


@router.post("", response_model=SkillResponse, status_code=201)
def add_student_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_student(current_user)

    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    skill = db.query(Skill).filter(Skill.skill_id == skill_data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing_skill = db.query(StudentSkill).filter(
        StudentSkill.student_id == student_profile.student_id,
        StudentSkill.skill_id == skill_data.skill_id,
    ).first()
    if existing_skill:
        raise HTTPException(status_code=400, detail="Skill already added")

    student_skill = StudentSkill(
        student_id=student_profile.student_id,
        skill_id=skill.skill_id,
        level=skill_data.level,
        source=skill_data.source,
    )

    db.add(student_skill)
    db.commit()
    db.refresh(student_skill)

    return SkillResponse(
        skill_id=skill.skill_id,
        skill_name=skill.skill_name,
        category=skill.category,
        description=skill.description,
        level=student_skill.level,
        source=student_skill.source,
    )


@router.delete("/{skill_id}", response_model=SkillResponse)
def delete_student_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_student(current_user)

    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    student_skill = db.query(StudentSkill).filter(
        StudentSkill.student_id == student_profile.student_id,
        StudentSkill.skill_id == skill_id,
    ).first()

    if not student_skill:
        raise HTTPException(status_code=404, detail="Student skill not found")

    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    deleted_skill = SkillResponse(
        skill_id=skill.skill_id,
        skill_name=skill.skill_name,
        category=skill.category,
        description=skill.description,
        level=student_skill.level,
        source=student_skill.source,
    )

    db.delete(student_skill)
    db.commit()

    return deleted_skill


@router.put("/{skill_id}", response_model=SkillResponse)
def update_student_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_student(current_user)

    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    student_skill = db.query(StudentSkill).filter(
        StudentSkill.student_id == student_profile.student_id,
        StudentSkill.skill_id == skill_id,
    ).first()

    if not student_skill:
        raise HTTPException(status_code=404, detail="Student skill not found")

    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    student_skill.level = skill_data.level
    student_skill.source = skill_data.source

    db.commit()
    db.refresh(student_skill)

    return SkillResponse(
        skill_id=skill.skill_id,
        skill_name=skill.skill_name,
        category=skill.category,
        description=skill.description,
        level=student_skill.level,
        source=student_skill.source,
    )
