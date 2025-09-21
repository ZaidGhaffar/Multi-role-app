from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .Pydantic_model import UserCreate, Token, UserResponse
from auth.utils import create_user, authenticate_user, get_company_by_name
from auth.dependencies import get_db
from core.security import create_access_token
from Database.database import Users

router = APIRouter()

# Signup
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_request: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.username == user_request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if company exists (employees can only join existing companies)
    company = get_company_by_name(db, user_request.company_name)
    if not company:
        raise HTTPException(
            status_code=400, 
            detail=f"No such company exists. Please contact your HR to create the company '{user_request.company_name}' first."
        )
    
    # Create user with existing company_id
    user = create_user(
        db=db, 
        username=user_request.username, 
        password=user_request.password,
        company_id=company.id
    )
    return user

# Login
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_data = {"sub": db_user.username, "role": db_user.role, "company_id": db_user.company_id}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}
