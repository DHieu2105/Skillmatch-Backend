from pydantic import BaseModel, EmailStr

class CompanyCreate(BaseModel):
    company_name: str
    description: str
    email: EmailStr
    phone: str
    website: str

class CompanyUpdate(BaseModel):
    company_name: str
    description: str
    email: EmailStr
    phone: str
    website: str

class CompanyResponse(CompanyCreate):
    company_id: int

    class Config:
        from_attributes = True
