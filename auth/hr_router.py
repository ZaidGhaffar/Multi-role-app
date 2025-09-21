from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import Pydantic_model, utils
from Database.database import SessionLocal,Users,Company
from core.security import create_access_token
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup", response_model=Pydantic_model.UserResponse)
def signup_hr(user: Pydantic_model.HRSignup, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.name == user.company_name.lower()).first()
    if company:
        raise HTTPException(status_code=400, detail="Company already exists")

    company = Company(name=user.company_name.lower())
    db.add(company)
    db.commit()
    db.refresh(company)

    db_user = Users(
        username=user.email,
        hashed_password=utils.hash_password(user.password),
        role="hr",
        company_id=company.id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Pydantic_model.Token)
def login_hr(user: Pydantic_model.HRLogin, db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.username == user.username, Users.role == "hr").first()
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid HR credentials")

    token_data = {"sub": db_user.username, "role": db_user.role, "company_id": db_user.company_id}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}
