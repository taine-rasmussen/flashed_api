from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    location: str
    home_gym: str | None = None
    grade_style: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime
    location: str
    home_gym: str | None = None
    grade_style: str


    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr | None = None

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str
