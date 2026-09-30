from pydantic import BaseModel


class CVDefaultUpdate(BaseModel):
    is_default: bool = True


class CVResponse(BaseModel):
    cv_id: int
    student_id: int
    file_name: str
    file_url: str
    parsed_text: str
    is_default: bool

    class Config:
        from_attributes = True