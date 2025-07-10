from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    profile_image_url = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String(50), nullable=False)
    home_gym = Column(String(50), nullable=True)
    grade_style = Column(String(50), nullable=False)
    onboarding_complete = Column(Boolean, default=False, nullable=False)
    auth_provider = Column(String(20), default='email', nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    climbs = relationship("Climb", back_populates="user")
    gyms = relationship("Gym", back_populates="user", cascade="all, delete-orphan")
    projects = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Climb(Base):
    __tablename__ = "climbs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    internal_grade = Column(Float, nullable=False, index=True)
    original_grade = Column(String, nullable=False)
    original_scale = Column(String(50), nullable=False)
    attempts = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="climbs")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    total_moves = Column(Integer, nullable=False, default=0)
    total_moves_completed = Column(Integer, nullable=False, default=0)
    notes = Column(ARRAY(Text), nullable=False, default=list)
    moves = Column(JSONB, nullable=False, default=list)
    sessions = Column(JSONB, nullable=False, default=list)
    user = relationship("User", back_populates="projects")

class Gym(Base):
    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="gyms")