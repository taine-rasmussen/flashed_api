from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional, Any, Dict


# ---------------------------
# Gym schemas
# ---------------------------

class GymBase(BaseModel):
    name: str
    is_default: Optional[bool] = False
    grade_ranges: Optional[List[Dict[str, int]]] = []   # ← NEW

class GymCreate(GymBase):
    pass

class GymResponse(GymBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------------------------
# User schemas
# ---------------------------

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: Optional[str] = None
    email: EmailStr
    password: str
    location: str
    home_gym: Optional[str] = None
    grade_style: str
    profile_image_url: Optional[str] = None
    auth_provider: str = "email"
    notifications_enabled: bool = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: Optional[str]
    email: EmailStr
    profile_image_url: Optional[str]
    created_at: datetime
    location: str
    home_gym: Optional[str]
    grade_style: str
    onboarding_complete: bool
    auth_provider: str
    notifications_enabled: bool
    gyms: Optional[List[GymResponse]] = []

    class Config:
        orm_mode = True


# ---------------------------
# Auth schemas
# ---------------------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr | None = None

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str


# ---------------------------
# Climb schemas
# ---------------------------

class ClimbBase(BaseModel):
    grade: str
    attempts: int

class ClimbCreate(BaseModel):
    # optional if not using custom grade range
    gym_id: Optional[int] = None 
    grade: str
    scale: str
    attempts: int

class ClimbResponse(ClimbBase):
    id: int
    created_at: datetime
    original_grade: str
    original_scale: str

    class Config:
        orm_mode = True

class ClimbFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    grade_range: Optional[List[str]] = None

class AverageGradeRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ---------------------------
# Project schemas
# ---------------------------

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
