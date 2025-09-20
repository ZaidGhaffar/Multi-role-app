from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .Pydantic_model import UserCreate, Token, UserResponse
from auth.utils import create_user, authenticate_user
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
    user = create_user(db, user_request.username, user_request.password)
    return user

# Login
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
