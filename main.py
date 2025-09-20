from fastapi import FastAPI, Depends
from auth.router import router as auth_router
from auth.dependencies import get_current_user
import uvicorn

app = FastAPI(title="Employee Auth API")

# Register Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Protected test route
@app.get("/me")
def read_current_user(user=Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
