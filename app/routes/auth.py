from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session  
from ..schemas.auth import RegisterRequest
from ..models.user import User
from ..core.database import get_db
from ..core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter()

@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    # ktra chùng email
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # hash mat khau
    hashed_password = hash_password(request.password)

    # tao tai khoan
    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        role=request.role,
        status="active",  # Set default status to active
        created_at=datetime.utcnow(),
        update_at=datetime.utcnow()
    )

    # Luu vao database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.user_id}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if user.status.upper() != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail="User account is not active"
        )

    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "role": user.role
        },
        expires_delta=30
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "status": current_user.status,
    }