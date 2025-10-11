# core/AI_Service.py
import time
import random
from typing import Dict, Tuple
from sqlalchemy.orm import Session
from Database.database import Video, Prediction

def EmotionModel(video_file_path: str) -> Dict[str, float]:
    """
    Dummy AI model function that simulates emotion predictions.
    Accepts a GCS signed URL and returns top 3 emotions with scores.
    """
    time.sleep(2)  # simulate processing

    emotions = ["happy", "sad", "angry", "stressed", "neutral", "excited", "calm", "frustrated"]
    scores = [random.uniform(0.1, 0.4) for _ in range(3)]
    total = sum(scores)
    scores = [s / total for s in scores]

    selected = random.sample(emotions, 3)
    return {selected[i]: round(scores[i], 3) for i in range(3)}

def compute_derived_fields(predictions: Dict[str, float]) -> Tuple[str, float]:
    """
    Compute top emotion and its score from predictions.
    """
    if not predictions:
        return None, None
    top_emotion = max(predictions, key=predictions.get)
    return top_emotion, predictions[top_emotion]

def process_video_with_ai(video_id: str, db: Session):
    """
    Fetch the video from DB, generate predictions, and store them.
    """
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        print(f"⚠️ Video {video_id} not found")
        return

    # ✅ 1. Get signed URL
    signed_url = video.gcs_url

    # ✅ 2. Get predictions from dummy AI
    predictions = EmotionModel(signed_url)

    # ✅ 3. Compute top emotion & score
    top_emotion, top_score = compute_derived_fields(predictions)

    # ✅ 4. Save predictions to DB
    for emotion, score in predictions.items():
        db.add(Prediction(video_id=video_id, emotion_label=emotion, score=score))

    video.is_processed = True
    db.commit()
    print(f"✅ Processed video {video_id} — {predictions}")
