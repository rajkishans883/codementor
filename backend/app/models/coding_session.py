# backend/app/models/coding_session.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CodingSession(Base):
    __tablename__ = "coding_sessions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)

    # Relations
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)

    # Session Info
    language = Column(String(50), nullable=False, default="python")  # python, javascript, java, cpp
    current_code = Column(Text, nullable=True)                       # Latest code written by user
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.IN_PROGRESS, nullable=False)

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="coding_sessions")
    problem = relationship("Problem", back_populates="coding_sessions")
    conversation = relationship("Conversation", back_populates="coding_session", uselist=False, cascade="all, delete-orphan")
    analysis_report = relationship("AnalysisReport", back_populates="coding_session", uselist=False, cascade="all, delete-orphan")
    # conversation = relationship("Conversation", back_populates="coding_session", uselist=False)
    submissions = relationship("Submission", back_populates="coding_session", cascade="all, delete-orphan")