from pydantic import BaseModel

class CompanyCreate(BaseModel):
    company_name: str
    description: str
    email: str
    phone: str
    website: str

class CompanyUpdate(BaseModel):
    company_name: str
    description: str
    email: str
    phone: str
    website: str

class CompanyResponse(CompanyCreate):
    company_id: int

    class Config:
        from_attributes = True
