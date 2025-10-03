from sqlalchemy import Column, String, create_engine, ForeignKey, DateTime, Boolean,Float
from sqlalchemy.orm import sessionmaker, relationship 
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

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
    created_at = Column(DateTime,default=datetime.utcnow)
    users = relationship("Users", back_populates="company")


# User Model
class Users(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, default= lambda: str(uuid.uuid4()))
    username = Column(String,nullable=False)
    email = Column(String, nullable=True)  # Add email field
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="employee")  # Store role in DB (employee/hr/etc.)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="users")
    videos = relationship("Video", back_populates="user")


class Video(Base):
    __tablename__ = 'videos'
    video_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    gcs_file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    
    user = relationship("Users", back_populates="videos")
    predictions = relationship("Prediction", back_populates="video")
    
    
class Prediction(Base):
    __tablename__ = 'predictions'
    
    prediction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey('videos.video_id'), nullable=False)
    emotion_label = Column(String, nullable=False)  # e.g., "stress", "happy", "neutral"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: Many Predictions belong to One Video
    video = relationship("Video", back_populates="predictions")
    


# Create tables
Base.metadata.create_all(engine)
