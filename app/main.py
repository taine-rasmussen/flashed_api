from fastapi import FastAPI, HTTPException, Depends, Body, Security, Request
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import models, schemas, crud, dev_routes
from .database import engine, Base, get_db
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime 
from jose import jwt
from .schemas import UserResponse
from jose.exceptions import JWTError
from fastapi.security import OAuth2PasswordBearer
from .utils import verify_password, hash_password
from typing import List, Optional
from sqlalchemy import func, case, cast, Integer
from .auth import get_current_user
from .conversion import convert_internal_to_display, convert_grade_to_internal, GradeStyle


app = FastAPI()

Base.metadata.create_all(bind=engine)

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 10080))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


if os.getenv("ENV") != "production":
    app.include_router(dev_routes.router)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")  
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return {"email": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")  
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return {"email": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")



# Routes

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": db_user.email, "id": db_user.id},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(
        data={"sub": db_user.email, "id": db_user.id},
        expires_delta=refresh_token_expires
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/refresh-token/")
def refresh_token(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token is required.")

    try:
        # Verify the refresh token
        token_data = verify_refresh_token(refresh_token)

        # Issue new access token
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": token_data["email"], "id": token_data["id"]},
            expires_delta=expires_delta,
        )

        # Rotate the refresh token
        new_refresh_token = create_refresh_token(
            data={"sub": token_data["email"], "id": token_data["id"]},
            expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")


@app.get("/protected-route/")
def protected_route(token: str = Depends(verify_access_token)):
    return {"message": f"Hello, {token}"}

@app.get("/get_user/", response_model=UserResponse)
def get_user(id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/update_user/", response_model=UserResponse)
def update_user(
    user_id: int = Body(...),
    updates: dict = Body(...),
    db: Session = Depends(get_db),
):
    updated_user = crud.update_user(db, user_id=user_id, updates=updates)
    return updated_user

@app.post("/change_password/", response_model=dict)
def change_password(
    data: schemas.ChangePasswordSchema,
    token: dict = Security(verify_access_token),
    db: Session = Depends(get_db)
):

    #Get the user from the db
    user_id = token.get("id")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the current password
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid current password")

    # Check if the new password is the same as the current password
    if verify_password(data.new_password, user.password_hash):
        raise HTTPException(status_code=400, detail="New password cannot be the same as the current password")

    # Hash the new password and update the user's password
    hashed_new_password = hash_password(data.new_password)
    user.password_hash = hashed_new_password
    db.commit()
    db.refresh(user)


    return {"message": "Password updated successfully"}

@app.post("/add_climb/", response_model=schemas.ClimbResponse)
def add_climb(
    climb: schemas.ClimbCreate,
    user_id: int,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_access_token)
):
    if token.get("id") != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to add climbs for this user.")

    try:
        internal_grade_value = convert_grade_to_internal(climb.grade, GradeStyle(climb.scale))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_climb = crud.create_climb(
        db=db,
        user_id=user_id,
        internal_grade=internal_grade_value,
        original_grade=climb.grade,
        original_scale=climb.scale,
        attempts=climb.attempts
    )

    return schemas.ClimbResponse(
        id=db_climb.id,
        grade=climb.grade,
        original_grade=db_climb.original_grade,
        original_scale=db_climb.original_scale,
        attempts=db_climb.attempts,
        created_at=db_climb.created_at
    )

@app.post("/get_climbs/", response_model=List[schemas.ClimbResponse])
def get_climbs(
    user_id: int,
    filters: schemas.ClimbFilter,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_access_token)
):
    if token.get("id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view climbs for this user.")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert the grade_range into internal values using user's grade style
    internal_grade_range = None
    if filters.grade_range:
        try:
            internal_grade_range = [
                convert_grade_to_internal(grade, GradeStyle(user.grade_style))
                for grade in filters.grade_range
            ]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    climbs = crud.get_user_climbs(db, user_id, filters, internal_grade_range)

    return [
        schemas.ClimbResponse(
            id=climb.id,
            grade=convert_internal_to_display(climb.internal_grade, GradeStyle(user.grade_style)),
            original_grade=climb.original_grade,
            original_scale=climb.original_scale,
            attempts=climb.attempts,
            created_at=climb.created_at
        )
        for climb in climbs
    ]

@app.post("/average_grade/")
def average_grade(
    request: schemas.AverageGradeRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_access_token)
):
    user_id = token.get("id")
    query = db.query(models.Climb).filter(models.Climb.user_id == user_id)
    
    if request.start_date:
        query = query.filter(models.Climb.created_at >= request.start_date)
    if request.end_date:
        query = query.filter(models.Climb.created_at <= request.end_date)
    
    # Convert V-grade strings to numeric values
    grade_numeric = case(
        (models.Climb.grade.like('V%'), cast(func.substr(models.Climb.grade, 2), Integer)),
        else_=None
    )
    
    avg_grade = query.with_entities(func.avg(grade_numeric)).scalar()
    
    # Round the average to the nearest whole number
    rounded_grade = round(avg_grade) if avg_grade is not None else 0
    
    # todo: take in grade style, convert font scale grades - how to average 8a, 8b+, 8c etc
    return {"average_grade": rounded_grade}


@app.get(
    "/projects/",
    response_model=List[schemas.ProjectResponse],
)
def read_projects(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_access_token),
):
    user_id = token_data["id"]
    projects = crud.get_user_projects(db, user_id)
    if projects is None:
        raise HTTPException(status_code=404, detail="No projects found")
    return projects

@app.post("/add_gym/", response_model=schemas.GymResponse)
def create_gym_for_user(
    gym: schemas.GymCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_gym(db, gym, current_user.id)

@app.get("/get_gyms/", response_model=List[schemas.GymResponse])
def read_user_gyms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_gyms(db, current_user.id)
