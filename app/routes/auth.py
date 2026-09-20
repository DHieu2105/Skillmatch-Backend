from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  
from ..schemas.auth import RegisterRequest
from ..models.user import User
from ..core.database import get_db
from ..core.security import hash_password

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