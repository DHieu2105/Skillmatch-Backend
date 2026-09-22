from pydantic import BaseModel


class CVCreate(BaseModel):
    file_name: str
    file_url: str
    parsed_text: str
    is_default: bool = False


class CVUpdate(BaseModel):
    file_name: str
    file_url: str
    parsed_text: str
    is_default: bool


class CVResponse(BaseModel):
    cv_id: int
    student_id: int
    file_name: str
    file_url: str
    parsed_text: str
    is_default: bool

    class Config:
        from_attributes = True