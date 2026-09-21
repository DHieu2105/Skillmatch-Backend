from fastapi import FastAPI

from app.routes import auth
from app.routes import students
from app.routes import skills

app = FastAPI()

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"]
)

app.include_router(
    students.router,
    prefix="/api/v1/students",
    tags=["students"]
)

app.include_router(
    skills.router,  
    prefix="/api/v1/skills",
    tags=["skills"]
)