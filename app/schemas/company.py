from pydantic import BaseModel, EmailStr

class CompanyCreate(BaseModel):
    company_name: str
    description: str
    email: EmailStr
    phone: str
    website: str
    address: str | None = None
    google_map_url: str | None = None
    logo_url: str | None = None
    company_size: str | None = None
    industry: str | None = None
    benefits: str | None = None

class CompanyUpdate(CompanyCreate):
    pass

class CompanyResponse(CompanyCreate):
    company_id: int

    class Config:
        from_attributes = True
