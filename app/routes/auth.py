from datetime import datetime, timedelta
import hashlib
import os
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  
from ..schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from ..models.password_reset_token import PasswordResetToken
from ..models.user import User
from ..core.database import get_db
from ..core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..services.email import send_password_reset_email
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

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
        auth_provider="local",
        role=request.role.value,
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
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.password_hash or not verify_password(request.password, user.password_hash):
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
        "auth_provider": current_user.auth_provider,
        "has_password": current_user.password_hash is not None,
    }


@router.put("/password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.password_hash:
        if not request.current_password:
            raise HTTPException(
                status_code=400,
                detail="Current password is required",
            )
        if not verify_password(request.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )

        message = "Password changed successfully"
    else:
        message = "Password set successfully"

    current_user.password_hash = hash_password(request.new_password)
    if current_user.auth_provider == "google":
        current_user.auth_provider = "local+google"
    current_user.update_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return {"message": message}


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if user and user.password_hash:
        raw_token = secrets.token_urlsafe(32)
        db.add(PasswordResetToken(
            user_id=user.user_id,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            created_at=datetime.utcnow(),
        ))
        db.commit()

        reset_url = os.getenv(
            "FRONTEND_RESET_PASSWORD_URL",
            "http://localhost:3000/reset-password",
        )
        send_password_reset_email(request.email, f"{reset_url}?token={raw_token}")

    return {
        "message": "If the email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used_at.is_(None),
    ).first()

    if not reset_token or reset_token.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.user_id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.password_hash = hash_password(request.new_password)
    reset_token.used_at = datetime.utcnow()
    user.update_at = datetime.utcnow()
    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/google")
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=503, detail="Google login is not configured")

    try:
        google_user = id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            client_id,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google credential")

    google_id = google_user.get("sub")
    email = google_user.get("email")
    if not google_id or not email or not google_user.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google account is not verified")

    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()

    if user:
        if user.google_id and user.google_id != google_id:
            raise HTTPException(status_code=409, detail="Google account is already linked")
        user.google_id = google_id
        user.auth_provider = "local+google" if user.password_hash else "google"
    else:
        if not request.role:
            raise HTTPException(
                status_code=400,
                detail="Role is required when creating a Google account",
            )
        user = User(
            email=email,
            password_hash=None,
            google_id=google_id,
            auth_provider="google",
            role=request.role.value,
            status="active",
            created_at=datetime.utcnow(),
            update_at=datetime.utcnow(),
        )
        db.add(user)

    if user.status.upper() != "ACTIVE":
        raise HTTPException(status_code=403, detail="User account is not active")

    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": str(user.user_id), "role": user.role},
        expires_delta=30,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
    }

