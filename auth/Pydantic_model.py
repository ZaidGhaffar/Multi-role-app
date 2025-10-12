from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    #username: str
    email: EmailStr # Added email field
    password: str
    company_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    user_id: str
    email: str
    role: str

    class Config:
        from_attributes = True

    
class HRSignup(BaseModel):
    email: EmailStr
    password: str
    company_name: str   # HR must create a company


class HRLogin(BaseModel):
    email: EmailStr
    password: str


class CreateVideo(BaseModel):
    original_filename: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    