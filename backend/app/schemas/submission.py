# backend/app/schemas/submission.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT = "time_limit"
    MEMORY_LIMIT = "memory_limit"


class SubmissionCreate(BaseModel):
    coding_session_id: int
    code: str
    language: str = "python"


class TestResultResponse(BaseModel):
    id: int
    test_case_id: int
    passed: bool
    actual_output: Optional[str] = None
    expected_output: Optional[str] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    id: int
    coding_session_id: int
    user_id: int
    problem_id: int
    code: str
    language: str
    status: SubmissionStatus
    passed_count: int
    total_count: int
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    test_results: List[TestResultResponse] = []

    class Config:
        from_attributes = True


class SubmissionSummaryResponse(BaseModel):
    id: int
    status: SubmissionStatus
    passed_count: int
    total_count: int
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True