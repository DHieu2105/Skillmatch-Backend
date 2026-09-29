from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.cv import CV
from ..models.application import Application
from ..schemas.cv import CVCreate, CVDefaultUpdate, CVResponse, CVUpdate

router = APIRouter()


def require_student(current_user: User):
    if current_user.role.upper() != "STUDENT":
        raise HTTPException(status_code=403, detail="Student role required")


def get_student_profile(current_user: User, db: Session) -> StudentProfile:
    require_student(current_user)
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()
    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student_profile


def clear_default_cvs(db: Session, student_id: int, excluded_cv_id: int | None = None):
    query = db.query(CV).filter(
        CV.student_id == student_id,
        CV.is_default.is_(True),
    )
    if excluded_cv_id is not None:
        query = query.filter(CV.cv_id != excluded_cv_id)
    for cv in query.all():
        cv.is_default = False


@router.get("", response_model=list[CVResponse])
def get_student_cvs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = get_student_profile(current_user, db)
    return db.query(CV).filter(CV.student_id == student_profile.student_id).all()


@router.post("", response_model=CVResponse, status_code=201)
def create_student_cv(
    cv_data: CVCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = get_student_profile(current_user, db)
    has_cv = db.query(CV).filter(CV.student_id == student_profile.student_id).first()
    is_default = cv_data.is_default or not has_cv
    if is_default:
        clear_default_cvs(db, student_profile.student_id)

    new_cv = CV(
        student_id=student_profile.student_id,
        file_name=cv_data.file_name,
        file_url=cv_data.file_url,
        parsed_text=cv_data.parsed_text,
        is_default=is_default,
    )
    db.add(new_cv)
    db.commit()
    db.refresh(new_cv)
    return new_cv


@router.put("/{cv_id}", response_model=CVResponse)
def update_student_cv(
    cv_id: int,
    cv_data: CVUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = get_student_profile(current_user, db)
    cv = db.query(CV).filter(
        CV.cv_id == cv_id,
        CV.student_id == student_profile.student_id,
    ).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv_data.is_default:
        clear_default_cvs(db, student_profile.student_id, cv.cv_id)
    elif cv.is_default:
        replacement = db.query(CV).filter(
            CV.student_id == student_profile.student_id,
            CV.cv_id != cv.cv_id,
        ).first()
        if replacement:
            replacement.is_default = True
        else:
            raise HTTPException(
                status_code=400,
                detail="A student must have a default CV",
            )

    cv.file_name = cv_data.file_name
    cv.file_url = cv_data.file_url
    cv.parsed_text = cv_data.parsed_text
    cv.is_default = cv_data.is_default
    db.commit()
    db.refresh(cv)
    return cv


@router.delete("/{cv_id}", response_model=CVResponse)
def delete_student_cv(
    cv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = get_student_profile(current_user, db)
    cv = db.query(CV).filter(
        CV.cv_id == cv_id,
        CV.student_id == student_profile.student_id,
    ).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if db.query(Application).filter(Application.cv_id == cv_id).first():
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a CV used by an application",
        )

    deleted_cv = CVResponse.model_validate(cv)
    replacement = None
    if cv.is_default:
        replacement = db.query(CV).filter(
            CV.student_id == student_profile.student_id,
            CV.cv_id != cv.cv_id,
        ).order_by(CV.cv_id).first()

    db.delete(cv)
    if replacement:
        replacement.is_default = True
    db.commit()
    return deleted_cv


@router.patch("/{cv_id}/default", response_model=CVResponse)
def set_default_cv(
    cv_id: int,
    default_data: CVDefaultUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = get_student_profile(current_user, db)
    cv = db.query(CV).filter(
        CV.cv_id == cv_id,
        CV.student_id == student_profile.student_id,
    ).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    if not default_data.is_default:
        raise HTTPException(status_code=400, detail="A CV must be set as default")

    clear_default_cvs(db, student_profile.student_id, cv.cv_id)
    cv.is_default = True
    db.commit()
    db.refresh(cv)
    return cv
