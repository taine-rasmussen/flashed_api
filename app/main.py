from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import models, schemas, crud
from .database import engine, Base, get_db

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    return crud.user_login(userLogin=user, db=db)
