from apscheduler.schedulers.background import BackgroundScheduler
from Database.database import SessionLocal, Video
from core.AI_Service import process_video_with_ai

def auto_process_pending_videos():
    """Check for unprocessed videos and process them."""
    db = SessionLocal()
    try:
        pending_videos = db.query(Video).filter(Video.is_processed == False).all()
        if not pending_videos:
            print("✅ No pending videos found.")
            return

        print(f"🎥 Found {len(pending_videos)} pending videos to process...")
        for v in pending_videos:
            # Directly call AI processing
            process_video_with_ai(v.video_id, db)
    except Exception as e:
        print(f"❌ Error in auto_process_pending_videos: {e}")
    finally:
        db.close()

def start_scheduler():
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_process_pending_videos, "interval", minutes=1)
    scheduler.start()
    print("🚀 Scheduler started (runs every 1 minute)")
