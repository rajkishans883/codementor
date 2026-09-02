# backend/app/models/analysis.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    
    coding_session_id = Column(
        Integer, 
        ForeignKey("coding_sessions.id", ondelete="CASCADE"), 
        nullable=False, 
        unique=True, 
        index=True
    )

    # Scores (out of 10)
    correctness_score = Column(Float, nullable=True)
    code_quality_score = Column(Float, nullable=True)
    edge_case_score = Column(Float, nullable=True)

    # Complexity
    time_complexity = Column(String(50), nullable=True)      # e.g. O(n)
    space_complexity = Column(String(50), nullable=True)     # e.g. O(1)

    # Detailed Analysis
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    optimization_suggestions = Column(Text, nullable=True)
    code_explanation = Column(Text, nullable=True)

    # Interview Questions (JSON string or plain text)
    interview_questions = Column(Text, nullable=True)

    # Full AI response (optional backup)
    full_report = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    coding_session = relationship("CodingSession", back_populates="analysis_report")