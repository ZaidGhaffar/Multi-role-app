from typing import Annotated
from fastapi import FastAPI, Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from auth.hr_router import router as hr_router
from auth.dependencies import get_current_user
import uvicorn
from auth.dependencies import get_db,uploader
from sqlalchemy.orm import Session
from auth.Pydantic_model import CreateVideo
from Database import Video

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
    return {"id": user.id, "username": user.username, "role": user.role}


@app.get("/generate_signed_url")
async def request_signed_url(filename:str,db: db_dependency):
    url = uploader.request_url(filename)
    return {"signed_url": url}

    
@app.post("/upload_complete")
async def upload_complete(upload_video: CreateVideo,db:db_dependency):
    new_video = Video(
        user_id=video.user_id,
        gcs_file_path=video.gcp_url,
        original_filename=video.original_filename
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return {
        "message": "Video metadata saved successfully",
        "video_id": new_video.video_id
    }


# 3️⃣ (Optional) Get Signed View URL for AI service
@app.get("/generate_view_url/{video_id}")
def generate_view_url(video_id: str, db: Session = Depends(get_db)):
    """
    Generate a signed URL so AI service (or user) can read the video.
    """
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    blob = uploader.bucket.blob(video.gcs_file_path)
    view_url = blob.generate_signed_url(
        version="v4",
        expiration=3600,  # 1 hour
        method="GET"
    )
    return {"view_url": view_url}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
