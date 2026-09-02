# backend/app/models/test_result.py

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    
    submission_id = Column(
        Integer, 
        ForeignKey("submissions.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    test_case_id = Column(
        Integer, 
        ForeignKey("problem_test_cases.id", ondelete="CASCADE"), 
        nullable=False
    )

    passed = Column(Boolean, default=False)
    actual_output = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    submission = relationship("Submission", back_populates="test_results")