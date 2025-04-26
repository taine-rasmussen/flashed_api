from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String(50), nullable=False)
    home_gym = Column(String(50), nullable=True)
    grade_style = Column(String(50), nullable=False)
    climbs = relationship("Climb", back_populates="user")
    projects = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Climb(Base):
    __tablename__ = "climbs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    grade = Column(String, index=True)
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