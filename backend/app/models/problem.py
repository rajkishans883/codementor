# backend/app/models/problem.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
import enum


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProblemType(str, enum.Enum):
    LEETCODE = "leetcode"          # AI-generated / interview style
    COMPETITIVE = "competitive"    # From Codeforces


class ProblemSource(str, enum.Enum):
    MANUAL = "manual"
    AI_GENERATED = "ai_generated"
    CODEFORCES = "codeforces"


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(SQLEnum(Difficulty), nullable=False, default=Difficulty.EASY)

    # Type & Source
    problem_type = Column(SQLEnum(ProblemType), nullable=False, default=ProblemType.LEETCODE)
    source = Column(SQLEnum(ProblemSource), nullable=False, default=ProblemSource.MANUAL)
    external_id = Column(String(100), nullable=True)   # Codeforces problem ID (e.g. "4A")

    # Content
    examples = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True)

    # Starter Codes
    starter_code_python = Column(Text, nullable=True)
    starter_code_javascript = Column(Text, nullable=True)
    starter_code_java = Column(Text, nullable=True)
    starter_code_cpp = Column(Text, nullable=True)
    function_name = Column(String(100), nullable=True)

    # For Competitive problems
    time_limit = Column(Float, nullable=True)      # in seconds
    memory_limit = Column(Integer, nullable=True)  # in MB

    # Status
    is_premium = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    coding_sessions = relationship("CodingSession", back_populates="problem")
    test_cases = relationship("ProblemTestCase", back_populates="problem", cascade="all, delete-orphan")