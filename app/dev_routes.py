from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models
from .utils import hash_password
from .database import get_db

router = APIRouter()

@router.post("/seed/", status_code=status.HTTP_201_CREATED)
def seed_data(db: Session = Depends(get_db)):
    try:
        # -----------------------------
        # Users
        # -----------------------------
        users = [
            models.User(
                first_name="Ella",
                last_name="Boulderson",
                email="ella@flashed.app",
                password_hash=hash_password("password123"),
                location="London, UK",
                home_gym="The Arch North",
                grade_style="V-Scale",
                username="ellab",
                profile_image_url=None,
                onboarding_complete=True,
                auth_provider="email",
                notifications_enabled=True,
            ),
            models.User(
                first_name="Tom",
                last_name="Slabsmith",
                email="tom@flashed.app",
                password_hash=hash_password("climbstrong"),
                location="London, UK",
                home_gym="Stronghold",
                grade_style="Font",
                username="tommy_slab",
                profile_image_url=None,
                onboarding_complete=True,
                auth_provider="email",
                notifications_enabled=True,
            ),
        ]

        for user in users:
            existing = db.query(models.User).filter_by(email=user.email).first()
            if not existing:
                db.add(user)
        db.commit()

        ella = db.query(models.User).filter_by(email="ella@flashed.app").first()
        tom = db.query(models.User).filter_by(email="tom@flashed.app").first()

        # -----------------------------
        # Climbs
        # -----------------------------
        climbs = [
            models.Climb(user_id=ella.id, grade="V3", attempts=1),
            models.Climb(user_id=ella.id, grade="V4", attempts=2),
            models.Climb(user_id=tom.id, grade="6B", attempts=3),
        ]
        db.add_all(climbs)

        # -----------------------------
        # Gyms
        # -----------------------------
        gym_data = [
            (ella, ["Beta Bloc", "VauxWall West", "The Arch North"]),
            (tom, ["Stronghold", "BlocHaus", "The Castle"]),
        ]

        for user, gym_names in gym_data:
            for gym_name in gym_names:
                exists = db.query(models.Gym).filter_by(user_id=user.id, name=gym_name).first()
                if not exists:
                    db.add(models.Gym(name=gym_name, user_id=user.id))

        # -----------------------------
        # Project
        # -----------------------------
        if not db.query(models.Project).filter_by(user_id=tom.id).first():
            db.add(models.Project(
                user_id=tom.id,
                is_active=True,
                total_moves=12,
                total_moves_completed=5,
                notes=[
                    "Struggling with overhang section",
                    "Improved footwork last session"
                ],
                moves=[
                    {"move": "heel hook start", "completed": True},
                    {"move": "compression on volume", "completed": False}
                ],
                sessions=[],
            ))

        db.commit()
        return {"message": "Seed data created with users, climbs, gyms, and project."}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Seed failed due to duplicate entries.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
