from pydantic import BaseModel, Field, model_validator
from enum import Enum
from pydantic import field_validator

class RegisterRole(str, Enum):
    STUDENT = "STUDENT"
    RECRUITER = "RECRUITER"

class RegisterRequest(BaseModel):
    role: RegisterRole = Field(
        ..., description="Required account role: STUDENT or RECRUITER"
    )
    email: str
    password: str

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class GoogleLoginRequest(BaseModel):
    credential: str
    role: RegisterRole | None = None

class ChangePasswordRequest(BaseModel):
    current_password: str | None = None
    new_password: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def validate_new_password(self):
        if self.current_password and self.current_password == self.new_password:
            raise ValueError("New password must be different from current password")
        return self
