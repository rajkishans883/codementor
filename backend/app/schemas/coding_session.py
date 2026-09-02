# backend/app/schemas/coding_session.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CodingSessionCreate(BaseModel):
    problem_id: int
    language: str = "python"


class CodingSessionUpdate(BaseModel):
    current_code: Optional[str] = None
    status: Optional[SessionStatus] = None
    language: Optional[str] = None


class CodingSessionResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    language: str
    current_code: Optional[str] = None
    status: SessionStatus
    started_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True