from fastapi import FastAPI

from app.routes import auth
from app.routes import students
from app.routes import skills
from app.routes import cvs
from app.routes import recruiters
from app.routes import companies

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

app.include_router(
    cvs.router, 
    prefix="/api/v1/cvs",
    tags=["cvs"]
)

app.include_router(
    recruiters.router,
    prefix="/api/v1/recruiters",
    tags=["recruiters"]
)

app.include_router(
    companies.router,
    prefix="/api/v1/companies",
    tags=["companies"]
)