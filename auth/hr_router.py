from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import Pydantic_model, utils
from auth.dependencies import get_db
from Database.database import Users,Company
from core.security import create_access_token
router = APIRouter()


@router.post("/signup", response_model=Pydantic_model.UserResponse)
def signup_hr(user: Pydantic_model.HRSignup, db: Session = Depends(get_db)):
    try:
        # Check if HR user already exists
        existing_hr = db.query(Users).filter(Users.email == user.email, Users.role == "hr").first()
        if existing_hr:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="HR account with this email already exists. Please use a different email or try logging in."
            )
        
        # Check if company already exists
        company = db.query(Company).filter(Company.name == user.company_name.lower()).first()
        if company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Company '{user.company_name}' already exists. Please choose a different company name."
            )

        # Create company
        company = Company(name=user.company_name.lower())
        db.add(company)
        db.commit()
        db.refresh(company)

        # Create HR user
        db_user = Users(
            email=user.email,
            hashed_password=utils.hash_password(user.password),
            role="hr",
            company_id=company.id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during HR registration. Please try again."
        )


@router.post("/login", response_model=Pydantic_model.Token)
def login_hr(user: Pydantic_model.HRLogin, db: Session = Depends(get_db)):
    try:
        # Check if HR user exists
        db_user = db.query(Users).filter(Users.email == user.email, Users.role == "hr").first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid HR credentials. Please check your email and password."
            )
        
        # Verify password
        if not utils.verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid HR credentials. Please check your email and password."
            )

        token_data = {"sub": db_user.email, "role": db_user.role, "company_id": db_user.company_id}
        access_token = create_access_token(token_data)
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during HR login. Please try again."
        )
