from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from . import models, schemas
from dotenv import load_dotenv
import os
from .utils import verify_password, hash_password



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# CRUD Functions
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password,
        location=user.location,
        home_gym=user.home_gym,
        grade_style=user.grade_style, 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def user_login(userLogin: schemas.UserLogin, db: Session):
    # Retrieve user by email
    user = get_user_by_email(db, userLogin.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Verify password
    if not verify_password(userLogin.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email},
    }

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user

def update_user(db: Session, user_id: int, updates: dict):
    # Fetch user by ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the email is being updated and ensure it's unique
    new_email = updates.get("email")
    if new_email and new_email != user.email:
        existing_user = get_user_by_email(db, new_email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")

    # Update fields dynamically
    for key, value in updates.items():
        if hasattr(user, key):
            setattr(user, key, value)

    # Commit changes
    db.commit()
    db.refresh(user)

    return user


def change_password(db: Session, user: models.User, curr_pwd: str, new_pwd: str):
    # Verify current password
    if not verify_password(curr_pwd, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # Hash new password
    hashed_new_pwd = hash_password(new_pwd)
    
    # Update password in database
    user.password_hash = hashed_new_pwd
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "Password updated successfully"}