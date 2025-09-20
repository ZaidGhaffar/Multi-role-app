from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker 
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

# User Model
class Users(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default= lambda: str(uuid.uuid4))
    username = Column(String,nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="employee")  # Store role in DB (employee/hr/etc.)

# Create tables
Base.metadata.create_all(engine)
