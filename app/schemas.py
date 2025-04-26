from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional, Any


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

class ClimbBase(BaseModel):
    grade: str
    attempts: int

class ClimbCreate(ClimbBase):
    pass

class ClimbResponse(ClimbBase):
    id: int
    created_at: datetime

class Config:
    orm_mode = True

class ClimbFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    grade_range: Optional[List[str]] = None

class AverageGradeRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    total_moves: int
    total_moves_completed: int
    notes: List[str]
    moves: List[dict[str, Any]]  
    sessions: List[dict[str, Any]]

    class Config:
        orm_mode = True

