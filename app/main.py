import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth
from app.routes import students
from app.routes import skills
from app.routes import cvs
from app.routes import recruiters
from app.routes import companies
from app.routes import jobs
from app.routes import job_skills
from app.routes import applications
from app.routes import recommendations
from app.routes import notifications

app = FastAPI()

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(
    jobs.router,
    prefix="/api/v1/jobs",
    tags=["jobs"]
)

app.include_router(
    job_skills.router,
    prefix="/api/v1/jobs",
    tags=["job skills"]
)

app.include_router(
    applications.router,
    prefix="/api/v1",
    tags=["applications"]
)

app.include_router(
    recommendations.router,
    prefix="/api/v1",
    tags=["recommendations"]
)

app.include_router(
    notifications.router,  
    prefix="/api/v1",
    tags=["notifications"]
)