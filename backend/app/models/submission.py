# backend/app/models/submission.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT = "time_limit"
    MEMORY_LIMIT = "memory_limit"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)

    coding_session_id = Column(
        Integer, 
        ForeignKey("coding_sessions.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)

    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)

    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    
    # Results summary
    passed_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    execution_time = Column(Float, nullable=True)      # in seconds
    memory_used = Column(Float, nullable=True)         # in MB
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    coding_session = relationship("CodingSession", back_populates="submissions")
    user = relationship("User")
    problem = relationship("Problem")
    test_results = relationship("TestResult", back_populates="submission", cascade="all, delete-orphan")