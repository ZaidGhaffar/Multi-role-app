from typing import Annotated
from fastapi import FastAPI, Depends,HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from auth.hr_router import router as hr_router
from auth.dependencies import get_current_user
import uvicorn
from auth.dependencies import get_db,uploader
from sqlalchemy.orm import Session
from auth.Pydantic_model import CreateVideo
from Database.database import Video

app = FastAPI(title="Employee Auth API")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Register Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(hr_router, prefix="/hr", tags=["Hr Authentication"]) 
db_dependency = Annotated[Session,Depends(get_db)]

@app.get("/")
def root():
    return {"message": "Welcome to Neurofy API 🚀"}
# Protected test route
@app.get("/me")
def read_current_user(user=Depends(get_current_user)):
    return {"id": user.user_id, "username": user.username, "role": user.role}


@app.get("/generate_signed_url")
async def request_signed_url(filename: str, db: db_dependency, content_type: str = "video/mp4"):
    url = uploader.request_url(filename, content_type=content_type)
    return {"signed_url": url}

    
@app.post("/upload_complete")
async def upload_complete(upload_video: CreateVideo, db: db_dependency, user=Depends(get_current_user)):
    # Generate a signed URL for the uploaded file
    blob = uploader.bucket.blob(upload_video.original_filename)
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=3600,  # 1 hour
        method="GET"
    )
    
    new_video = Video(
        user_id=user.user_id,
        gcs_url=signed_url,
        original_filename=upload_video.original_filename
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return {
        "message": "Video metadata saved successfully",
        "video_id": new_video.video_id
    }

# List current user's videos (basic upload history)
@app.get("/my/videos")
def list_my_videos(db: db_dependency, user=Depends(get_current_user)):
    videos = db.query(Video).filter(Video.user_id == user.user_id).order_by(Video.upload_timestamp.desc()).all()
    return [
        {
            "video_id": v.video_id,
            "gcs_url": v.gcs_url,
            "original_filename": v.original_filename,
            "upload_timestamp": v.upload_timestamp.isoformat() if v.upload_timestamp else None,
            "is_processed": v.is_processed,
        }
        for v in videos
    ]


# 3️⃣ (Optional) Get Signed View URL for AI service
@app.get("/generate_view_url/{video_id}")
def generate_view_url(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Return the stored signed URL directly since we're now storing signed URLs
    return {"view_url": video.gcs_url}


# Direct upload endpoint to avoid browser CORS on signed URL PUT
@app.post("/upload_direct")
async def upload_direct(file: UploadFile = File(...), user=Depends(get_current_user)):
    try:
        blob = uploader.bucket.blob(file.filename)
        blob.upload_from_file(file.file, content_type=file.content_type)
        
        # Generate a signed URL for the uploaded file
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=3600,  # 1 hour
            method="GET"
        )
        
        return {"gcs_url": signed_url, "original_filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
