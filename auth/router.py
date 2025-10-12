from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .Pydantic_model import UserCreate, Token, UserResponse, LoginRequest
from auth.utils import create_user, authenticate_user, get_company_by_name
from auth.dependencies import get_db
from core.security import create_access_token
from Database.database import Users

router = APIRouter()

# Signup
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_request: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(Users).filter(Users.email == user_request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered. Please use a different email or try logging in."
            )
        
        # Check if company exists (employees can only join existing companies)
        company = get_company_by_name(db, user_request.company_name)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Company '{user_request.company_name}' does not exist. Please contact your HR to create the company first."
            )
        
        # Create user with existing company_id
        user = create_user(
            db=db, 
            email=user_request.email,
            password=user_request.password,
            company_id=company.id
        )
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during user registration. Please try again."
        )

# Login
@router.post("/token", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        user = db.query(Users).filter(Users.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )
        
        # Authenticate user
        db_user = authenticate_user(db, login_data.email, login_data.password)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )

        token_data = {"sub": db_user.email, "role": db_user.role, "company_id": db_user.company_id}
        access_token = create_access_token(token_data)
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )
