from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.company import Company
from ..models.user import User
from ..schemas.company import CompanyCreate, CompanyResponse

router = APIRouter()


def require_recruiter(current_user: User):
    if current_user.role.upper() != "RECRUITER":
        raise HTTPException(status_code=403, detail="Recruiter role required")


@router.post("", response_model=CompanyResponse)
def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_recruiter(current_user)

    company = Company(
        company_name=company_data.company_name,
        description=company_data.description,
        email=company_data.email,
        phone=company_data.phone,
        website=company_data.website,
        created_at=datetime.utcnow(),
        update_at=datetime.utcnow(),
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_recruiter(current_user)

    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_recruiter(current_user)

    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.company_name = company_data.company_name
    company.description = company_data.description
    company.email = company_data.email
    company.phone = company_data.phone
    company.website = company_data.website
    company.update_at = datetime.utcnow()

    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}", response_model=CompanyResponse)
def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_recruiter(current_user)

    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()
    return company
