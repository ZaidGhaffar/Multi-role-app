from sqlalchemy import Column, String, create_engine, ForeignKey, DateTime, func
from sqlalchemy.orm import sessionmaker, relationship 
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import uuid

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String,unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    users = relationship("Users", back_populates="company")




# User Model
class Users(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default= lambda: str(uuid.uuid4()))
    username = Column(String,nullable=False)
    email = Column(String, nullable=True)  # Add email field
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="employee")  # Store role in DB (employee/hr/etc.)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="users")

# Create tables
Base.metadata.create_all(engine)
