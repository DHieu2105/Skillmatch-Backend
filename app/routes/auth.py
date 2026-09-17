from ..schemas.auth import RegisterRequest
from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login():
    return {"message": "Login successful"}  

@router.post("/register")
def register(request: RegisterRequest):
    return {"message": "Registration successful"}