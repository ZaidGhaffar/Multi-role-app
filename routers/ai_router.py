from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from Database.database import get_db, Video, Prediction
from auth.dependencies import get_current_user
from core.AI_Service import process_video_with_ai, compute_derived_fields  # ✅ imported from new service

router = APIRouter()

@router.post("/process-video/{video_id}")
async def trigger_video_processing(
    video_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Trigger AI processing for a specific video in the background.
    """
    video = db.query(Video).filter(
        Video.video_id == video_id,
        Video.user_id == user.user_id
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.is_processed:
        raise HTTPException(status_code=400, detail="Video already processed")

    # ✅ Add background task to process video
    background_tasks.add_task(process_video_with_ai, video_id, db)

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
    Get AI emotion predictions for a specific video.
    """
    video = db.query(Video).filter(
        Video.video_id == video_id,
        Video.user_id == user.user_id
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

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

    # ✅ Compute top emotion and score from predictions
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
    pending_videos = db.query(Video).filter(
        Video.user_id == user.user_id,
        Video.is_processed == False
    ).all()

    if not pending_videos:
        return {
            "message": "No pending videos to process",
            "count": 0
        }

    # ✅ Add background tasks for each pending video
    for video in pending_videos:
        background_tasks.add_task(process_video_with_ai, video.video_id, db)

    return {
        "message": f"Started processing {len(pending_videos)} videos",
        "count": len(pending_videos),
        "video_ids": [v.video_id for v in pending_videos]
    }
