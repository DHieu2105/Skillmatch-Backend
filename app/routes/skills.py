from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.skill import Skill
from ..models.student_skill import StudentSkill
from ..schemas.skill import SkillCreate, SkillResponse

router = APIRouter()


@router.get("/skills", response_model=list[SkillResponse])
def get_student_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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


@router.post("/skills", response_model=SkillResponse)
def add_student_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    skill = db.query(Skill).filter(Skill.skill_id == skill_data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

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


@router.delete("/skills/{skill_id}", response_model=SkillResponse)
def delete_student_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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


@router.put("/skills/{skill_id}", response_model=SkillResponse)
def update_student_skill(
    skill_id: int,
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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