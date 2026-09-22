from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.student_profile import StudentProfile
from ..models.cv import CV
from ..schemas.cv import CVCreate, CVUpdate, CVResponse

router = APIRouter()

@router.get("/cv", response_model=CVResponse | None)
def get_student_cv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        return None

    cv = db.query(CV).filter(CV.student_id == student_profile.student_id).first()
    if not cv:
        return None

    return CVResponse(
        cv_id=cv.cv_id,
        student_id=cv.student_id,
        file_name=cv.file_name,
        file_url=cv.file_url,
        parsed_text=cv.parsed_text,
        is_default=cv.is_default,
    )

@router.post("/cv", response_model=CVCreate)
def create_student_cv(  
    cv_data: CVCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    new_cv = CV(
        student_id=student_profile.student_id,
        file_name=cv_data.file_name,
        file_url=cv_data.file_url,
        parsed_text=cv_data.parsed_text,
        is_default=cv_data.is_default,
    )

    db.add(new_cv)
    db.commit()
    db.refresh(new_cv)

    return CVCreate(
        file_name=new_cv.file_name,
        file_url=new_cv.file_url,
        parsed_text=new_cv.parsed_text,
        is_default=new_cv.is_default,
    )

@router.put("/cv", response_model=CVCreate)
def update_student_cv(
    cv_data: CVUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    cv = db.query(CV).filter(CV.student_id == student_profile.student_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    cv.file_name = cv_data.file_name
    cv.file_url = cv_data.file_url
    cv.parsed_text = cv_data.parsed_text
    cv.is_default = cv_data.is_default

    db.commit()
    db.refresh(cv)

    return CVCreate(
        file_name=cv.file_name,
        file_url=cv.file_url,
        parsed_text=cv.parsed_text,
        is_default=cv.is_default,
    )

@router.delete("/cv", response_model=CVResponse)
def delete_student_cv( 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    cv = db.query(CV).filter(CV.student_id == student_profile.student_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    deleted_cv = CVResponse(
        cv_id=cv.cv_id,
        student_id=cv.student_id,
        file_name=cv.file_name,
        file_url=cv.file_url,
        parsed_text=cv.parsed_text,
        is_default=cv.is_default,
    )

    db.delete(cv)
    db.commit()

    return deleted_cv
@router.get("/cv/default", response_model=CVResponse | None)
def get_default_student_cv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.user_id
    ).first()

    if not student_profile:
        return None

    cv = db.query(CV).filter(
        CV.student_id == student_profile.student_id,
        CV.is_default == True
    ).first()

    if not cv:
        return None

    return CVResponse(
        cv_id=cv.cv_id,
        student_id=cv.student_id,
        file_name=cv.file_name,
        file_url=cv.file_url,
        parsed_text=cv.parsed_text,
        is_default=cv.is_default,
    )