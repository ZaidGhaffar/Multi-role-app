from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from auth.hr_router import router as hr_router
from auth.dependencies import get_current_user
import uvicorn

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

@app.get("/")
def root():
    return {"message": "Welcome to Neurofy API 🚀"}
# Protected test route
@app.get("/me")
def read_current_user(user=Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
