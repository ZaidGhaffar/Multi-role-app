from sqlalchemy.orm import Session
from Database.database import Users
from core.security import hash_password, verify_password

def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()

def create_user(db: Session, username: str, password: str, role: str = "employee"):
    user = Users(
        username=username,
        hashed_password=hash_password(password),
        role=role
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
