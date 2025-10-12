from sqlalchemy.orm import Session
from Database.database import Users, Company
from core.security import hash_password, verify_password

def get_user_by_username(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def get_company_by_name(db: Session, company_name: str):
    """Get company by name if it exists, return None if not found"""
    return db.query(Company).filter(Company.name == company_name.lower()).first()

def get_or_create_company(db: Session, company_name: str):
    """Get existing company or create new one (used for HR signup)"""
    # Check if company already exists (case insensitive)
    company = db.query(Company).filter(Company.name == company_name.lower()).first()
    if company:
        return company
    
    # Create new company
    company = Company(name=company_name.lower())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def create_user(db: Session, email: str, password: str, company_id: str, role: str = "employee"):
    user = Users(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        company_id=company_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_username(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

