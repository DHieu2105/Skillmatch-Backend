import pymupdf
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pathlib import PurePosixPath
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.cv import CV
from ..models.application import Application
from ..nlp.cv_parser import extract_pdf_text
from ..schemas.cv import CVDefaultUpdate, CVResponse, CVUpdate
from ..services.storage import (
    StorageConfigurationError,
    StorageUploadError,
    upload_cv_pdf,
)

router = APIRouter()
MAX_CV_FILE_SIZE = 10 * 1024 * 1024


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
    file: UploadFile = File(...),
    is_default: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = get_student_profile(current_user, db)

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    file_name = PurePosixPath(
        (file.filename or "cv.pdf").replace("\\", "/").strip()
    ).name
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    file_content = file.file.read()
    if len(file_content) > MAX_CV_FILE_SIZE:
        raise HTTPException(status_code=413, detail="CV file must be 10 MB or smaller")
    if not file_content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")

    try:
        parsed_text = extract_pdf_text(file_content)
    except (pymupdf.FileDataError, RuntimeError) as error:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF") from error
    if not parsed_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF")

    try:
        file_url = upload_cv_pdf(file_name, file_content)
    except StorageConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except StorageUploadError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    has_cv = db.query(CV).filter(CV.student_id == student_profile.student_id).first()
    should_be_default = is_default or not has_cv
    if should_be_default:
        clear_default_cvs(db, student_profile.student_id)

    new_cv = CV(
        student_id=student_profile.student_id,
        file_name=file_name,
        file_url=file_url,
        parsed_text=parsed_text,
        is_default=should_be_default,
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
