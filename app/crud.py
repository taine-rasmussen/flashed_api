from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from fastapi import HTTPException
from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password,
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
    if not bcrypt.verify(userLogin.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": user.id}
