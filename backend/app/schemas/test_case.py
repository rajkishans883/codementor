# backend/app/schemas/test_case.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TestCaseCreate(BaseModel):
    problem_id: int
    input_data: str
    expected_output: str
    is_hidden: bool = False
    order: int = 0
    explanation: Optional[str] = None


class TestCaseResponse(BaseModel):
    id: int
    problem_id: int
    input_data: str
    expected_output: str
    is_hidden: bool
    order: int
    explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TestCasePublicResponse(BaseModel):
    """Only visible test cases (for students)"""
    id: int
    input_data: str
    expected_output: str
    order: int
    explanation: Optional[str] = None

    class Config:
        from_attributes = True