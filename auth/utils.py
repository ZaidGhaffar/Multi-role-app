from sqlalchemy.orm import Session
from Database.database import Users, Company
from core.security import hash_password, verify_password

def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()

def get_or_create_company(db: Session, company_name: str):
    # Check if company already exists
    company = db.query(Company).filter(Company.name == company_name).first()
    if company:
        return company
    
    # Create new company
    company = Company(name=company_name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def create_user(db: Session, username: str, password: str, company_id: str, email: str = None, role: str = "employee"):
    user = Users(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        company_id=company_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

