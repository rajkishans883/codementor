# backend/app/routes/analysis.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.coding_session import CodingSession
from app.models.problem import Problem
from app.models.analysis import AnalysisReport
from app.schemas.analysis import AnalysisReportResponse
from app.middleware.auth import get_current_user
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/sessions/{session_id}", response_model=AnalysisReportResponse)
def generate_analysis(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate analysis report for a coding session"""

    # Get session
    session = db.query(CodingSession).filter(
        CodingSession.id == session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.current_code:
        raise HTTPException(status_code=400, detail="No code found in this session")

    # Check if report already exists
    existing = db.query(AnalysisReport).filter(
        AnalysisReport.coding_session_id == session_id
    ).first()

    if existing:
        return existing

    # Get problem
    problem = db.query(Problem).filter(Problem.id == session.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Generate report using AI
    report_data = ai_service.generate_analysis_report(problem, session)

    # Save to database
    report = AnalysisReport(
        coding_session_id=session_id,
        **report_data
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get("/sessions/{session_id}", response_model=AnalysisReportResponse)
def get_analysis(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get existing analysis report"""

    session = db.query(CodingSession).filter(
        CodingSession.id == session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    report = db.query(AnalysisReport).filter(
        AnalysisReport.coding_session_id == session_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Analysis report not found")

    return report