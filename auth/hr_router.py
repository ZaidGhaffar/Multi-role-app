from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from auth import Pydantic_model, utils
from auth.dependencies import get_db
from Database.database import Users,Company
from core.security import create_access_token
import logging
logger = logging.getLogger(__name__)
router = APIRouter()
from datetime import datetime, timedelta


@router.post("/signup", response_model=Pydantic_model.UserResponse)
def signup_hr(user: Pydantic_model.HRSignup, db: Session = Depends(get_db)):
    logger.info(f"📩 Signup API called from frontend with: {user.email}, {user.company_name}")
    print("✅ Frontend reached /hr/signup route with:", user.dict())
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



@router.get("/dashboard/employee-department")
def get_employee_departments():
    # For testing, return dummy data
    return {
  "total_employees": 15,
  "departments": [
    { "name": "HR", "count": 3 },
    { "name": "Engineering", "count": 8 },
    { "name": "Finance", "count": 4 }
  ]
}

@router.get("/dashboard/summary")
def get_hr_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns top-level HR metrics summary (total employees, active, departments, etc.)
    """
    summary_data = {
        "total_employees": 50,
        "active_employees": 47,
        "departments": 5,
        "new_hires": 3,
        "resigned": 1,
        "attendance_rate": 92.5,
        "average_emotion_score": 7.8,
    }
    return summary_data


@router.get("/dashboard/emotion-distribution")
def get_emotion_distribution(db: Session = Depends(get_db)):
    """
    Returns emotion distribution across employees (bar chart data)
    """
    emotions = [
        {"emotion": "Happy", "count": 20},
        {"emotion": "Neutral", "count": 15},
        {"emotion": "Sad", "count": 10},
        {"emotion": "Stressed", "count": 3},
        {"emotion": "Angry", "count": 2},
    ]
    return {"total": sum(e["count"] for e in emotions), "data": emotions}


@router.get("/dashboard/emotion-pie-distribution")
def get_emotion_pie_distribution(db: Session = Depends(get_db)):
    """
    Returns percentage distribution for emotion pie chart
    """
    emotions = {
        "Happy": 40,
        "Neutral": 30,
        "Sad": 20,
        "Stressed": 5,
        "Angry": 5
    }
    return emotions


@router.get("/dashboard/emotion-trend")
def get_emotion_trend(days: int = Query(30, description="Number of days to show"), db: Session = Depends(get_db)):
    """
    Returns time-series trend of emotion scores over N days
    """
    today = datetime.utcnow()
    data = []

    for i in range(days):
        date = today - timedelta(days=i)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "average_score": round(6.5 + (i % 5) * 0.3, 2),  # Mock trend
        })

    return list(reversed(data))


@router.get("/employees")
def get_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns a paginated list of employees.
    """
    # 🔹 Dummy data (replace with DB query)
    all_employees = [
        {"id": 1, "name": "Ali Khan", "department": "HR", "designation": "HR Officer", "status": "Active"},
        {"id": 2, "name": "Sara Ahmed", "department": "Finance", "designation": "Accountant", "status": "Active"},
        {"id": 3, "name": "Ahmed Raza", "department": "Engineering", "designation": "Software Engineer", "status": "On Leave"},
        {"id": 4, "name": "Fatima Noor", "department": "Marketing", "designation": "Manager", "status": "Active"},
        {"id": 5, "name": "Usman Ali", "department": "IT", "designation": "Network Admin", "status": "Inactive"},
        {"id": 6, "name": "Zainab Tariq", "department": "HR", "designation": "Recruiter", "status": "Active"},
        {"id": 7, "name": "Bilal Hussain", "department": "Finance", "designation": "Analyst", "status": "Active"},
        {"id": 8, "name": "Maryam Shah", "department": "Engineering", "designation": "DevOps", "status": "Active"},
        {"id": 9, "name": "Hassan Ali", "department": "Engineering", "designation": "Backend Dev", "status": "Active"},
        {"id": 10, "name": "Ayesha Khan", "department": "Design", "designation": "UI/UX Designer", "status": "Active"},
        {"id": 11, "name": "Imran Nazir", "department": "HR", "designation": "Assistant", "status": "Inactive"},
    ]

    # 🔹 Pagination logic
    start = (page - 1) * page_size
    end = start + page_size
    paginated_employees = all_employees[start:end]

    return {
        "page": page,
        "page_size": page_size,
        "total": len(all_employees),
        "employees": paginated_employees
    }