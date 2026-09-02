# backend/app/schemas/analysis.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnalysisReportResponse(BaseModel):
    id: int
    coding_session_id: int
    correctness_score: Optional[float] = None
    code_quality_score: Optional[float] = None
    edge_case_score: Optional[float] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    optimization_suggestions: Optional[str] = None
    code_explanation: Optional[str] = None
    interview_questions: Optional[str] = None
    full_report: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True