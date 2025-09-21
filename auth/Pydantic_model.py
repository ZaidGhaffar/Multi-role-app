from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    password: str
    company_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    username: str
    role: str

    class Config:
        orm_mode = True

    
class HRSignup(BaseModel):
    email: EmailStr
    password: str
    company_name: str   # HR must create a company


class HRLogin(BaseModel):
    username: EmailStr
    password: str


