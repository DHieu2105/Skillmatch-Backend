from pydantic import BaseModel
from enum import Enum

class RegisterRole(str, Enum):
    STUDENT = "STUDENT"
    RECRUITER = "RECRUITER"

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: RegisterRole