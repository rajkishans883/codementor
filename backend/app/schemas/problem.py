# backend/app/schemas/problem.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProblemType(str, Enum):
    LEETCODE = "leetcode"
    COMPETITIVE = "competitive"


class ProblemSource(str, Enum):
    MANUAL = "manual"
    AI_GENERATED = "ai_generated"
    CODEFORCES = "codeforces"


# ========== Response Schema ==========
class ProblemResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    difficulty: Difficulty
    problem_type: ProblemType
    source: ProblemSource
    examples: Optional[str] = None
    constraints: Optional[str] = None
    tags: Optional[str] = None
    starter_code_python: Optional[str] = None
    starter_code_javascript: Optional[str] = None
    starter_code_java: Optional[str] = None
    starter_code_cpp: Optional[str] = None
    time_limit: Optional[float] = None
    memory_limit: Optional[int] = None
    is_premium: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== List Response ==========
class ProblemListResponse(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: Difficulty
    problem_type: ProblemType
    tags: Optional[str] = None
    is_premium: bool

    class Config:
        from_attributes = True