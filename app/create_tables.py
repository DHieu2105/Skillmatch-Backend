from app.core.database import Base, engine

from app.models import application
from app.models import user
from app.models import student_skill
from app.models import skill
from app.models import company
from app.models import job
from app.models import job_skill
from app.models import cv
from app.models import recommendation
from app.models import recruiter_profile
from app.models import student_profile
from app.models import notification

Base.metadata.create_all(bind=engine)