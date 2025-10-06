from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List
import random
import time
from Database.database import get_db, Video, Prediction
from auth.dependencies import get_current_user
from core.VideoUploader import VideoUploader
import requests
import json

router = APIRouter()

# Initialize VideoUploader for GCS operations
uploader = VideoUploader()

def EmotionModel(video_file_path: str) -> Dict[str, float]:
    """
    Dummy AI model function that simulates emotion predictions.
    This function accepts a video file path (from GCS signed URL) and returns
    dummy top 3 emotions and scores in the form of a dictionary.
    
    Args:
        video_file_path (str): GCS signed URL or file path
        
    Returns:
        Dict[str, float]: Dictionary with emotion labels and their confidence scores
    """
    # Simulate processing time
    time.sleep(2)
    
    # Define possible emotions
    emotions = ["happy", "sad", "angry", "stressed", "neutral", "excited", "calm", "frustrated"]
    
    # Generate random scores that sum to approximately 1.0
    scores = [random.uniform(0.1, 0.4) for _ in range(3)]
    total = sum(scores)
    scores = [score / total for score in scores]  # Normalize to sum to 1.0
    
    # Select random emotions
    selected_emotions = random.sample(emotions, 3)
    
    # Create predictions dictionary
    predictions = {
        selected_emotions[0]: round(scores[0], 3),
        selected_emotions[1]: round(scores[1], 3),
        selected_emotions[2]: round(scores[2], 3)
    }
    
    return predictions

def compute_derived_fields(predictions: Dict[str, float]) -> tuple:
    """
    Compute derived fields from predictions.
    
    Args:
        predictions (Dict[str, float]): Dictionary with emotion labels and scores
        
    Returns:
        tuple: (top_emotion, top_score)
    """
    if not predictions:
        return None, None
    
    top_emotion = max(predictions, key=predictions.get)
    top_score = predictions[top_emotion]
    
    return top_emotion, top_score

async def process_video_ai(video_id: str, db: Session):
    """
    Background task to process video with AI model.
    
    Args:
        video_id (str): ID of the video to process
        db (Session): Database session
    """
    try:
        # Get video from database
        video = db.query(Video).filter(Video.video_id == video_id).first()
        if not video:
            print(f"Video {video_id} not found")
            return
        
        # Get signed URL for the video
        view_url = video.gcs_url
        
        # Call AI model (dummy implementation)
        predictions = EmotionModel(view_url)
        
        # Compute derived fields
        top_emotion, top_score = compute_derived_fields(predictions)
        
        # Store predictions in database
        for emotion, score in predictions.items():
            prediction = Prediction(
                video_id=video_id,
                emotion_label=emotion,
                score=score
            )
            db.add(prediction)
        
        # Update video status to processed
        video.is_processed = True
        db.commit()
        
        print(f"Successfully processed video {video_id} with predictions: {predictions}")
        
    except Exception as e:
        print(f"Error processing video {video_id}: {str(e)}")
        db.rollback()

@router.post("/process-video/{video_id}")
async def trigger_video_processing(
    video_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Trigger AI processing for a specific video.
    This endpoint starts the background processing task.
    """
    # Check if video exists and belongs to the user
    video = db.query(Video).filter(
        Video.video_id == video_id,
        Video.user_id == user.user_id
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.is_processed:
        raise HTTPException(status_code=400, detail="Video already processed")
    
    # Add background task
    background_tasks.add_task(process_video_ai, video_id, db)
    
    return {
        "message": "Video processing started",
        "video_id": video_id,
        "status": "processing"
    }

@router.get("/video/{video_id}/predictions")
async def get_video_predictions(
    video_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get predictions for a specific video.
    """
    # Check if video exists and belongs to the user
    video = db.query(Video).filter(
        Video.video_id == video_id,
        Video.user_id == user.user_id
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get predictions
    predictions = db.query(Prediction).filter(
        Prediction.video_id == video_id
    ).all()
    
    if not predictions:
        return {
            "video_id": video_id,
            "is_processed": video.is_processed,
            "predictions": [],
            "top_emotion": None,
            "top_score": None
        }
    
    # Format predictions
    prediction_dict = {p.emotion_label: p.score for p in predictions}
    top_emotion, top_score = compute_derived_fields(prediction_dict)
    
    return {
        "video_id": video_id,
        "is_processed": video.is_processed,
        "predictions": prediction_dict,
        "top_emotion": top_emotion,
        "top_score": top_score
    }

@router.post("/process-all-pending")
async def process_all_pending_videos(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Process all pending videos for the current user.
    """
    # Get all unprocessed videos for the user
    pending_videos = db.query(Video).filter(
        Video.user_id == user.user_id,
        Video.is_processed == False
    ).all()
    
    if not pending_videos:
        return {
            "message": "No pending videos to process",
            "count": 0
        }
    
    # Add background tasks for each video
    for video in pending_videos:
        background_tasks.add_task(process_video_ai, video.video_id, db)
    
    return {
        "message": f"Started processing {len(pending_videos)} videos",
        "count": len(pending_videos),
        "video_ids": [v.video_id for v in pending_videos]
    }
