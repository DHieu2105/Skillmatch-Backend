from pydantic import BaseModel, Field
from enum import Enum
from pydantic import field_validator

class RegisterRole(str, Enum):
    STUDENT = "STUDENT"
    RECRUITER = "RECRUITER"

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: RegisterRole = Field(
        ..., description="Required account role: STUDENT or RECRUITER"
    )

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

class LoginRequest(BaseModel):
    email: str
    password: str