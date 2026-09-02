# backend/app/models/problem_test_case.py

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ProblemTestCase(Base):
    __tablename__ = "problem_test_cases"

    id = Column(Integer, primary_key=True, index=True)
    
    problem_id = Column(
        Integer, 
        ForeignKey("problems.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )

    # Test case data (JSON as text for now)
    input_data = Column(Text, nullable=False)          # e.g. {"nums": [2,7,11,15], "target": 9}
    expected_output = Column(Text, nullable=False)     # e.g. [0,1]
    
    is_hidden = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0)                 # Display order
    explanation = Column(String(500), nullable=True)   # Optional explanation

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    problem = relationship("Problem", back_populates="test_cases")