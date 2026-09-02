# backend/app/models/user.py

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    Enum as SQLEnum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    # ======================
    # Primary Key
    # ======================
    id = Column(Integer, primary_key=True, index=True)

    # ======================
    # Authentication Fields
    # ======================
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # ======================
    # Profile Information
    # ======================
    full_name = Column(String(150), nullable=False)
    username = Column(String(50), unique=True, nullable=True, index=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # ======================
    # Account Status
    # ======================
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)

    # ======================
    # Preferences / Settings
    # ======================
    preferred_language = Column(String(50), default="python")   # python, javascript, etc.
    theme = Column(String(20), default="dark")                  # dark / light
    email_notifications = Column(Boolean, default=True)

    # ======================
    # Usage Tracking (Useful for monetization later)
    # ======================
    total_analyses = Column(Integer, default=0)
    total_reviews = Column(Integer, default=0)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # ======================
    # Timestamps
    # ======================
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ======================
    # Relationships (for fut
    # messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    # code_snippets = relationship("CodeSnippet", back_populates="user", cascade="all, delete-orphan")
    code_snippets = relationship("CodeSnippet", back_populates="user", cascade="all, delete-orphan")
    coding_sessions = relationship("CodingSession", back_populates="user", cascade="all, delete-orphan")