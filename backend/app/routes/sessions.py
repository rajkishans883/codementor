# backend/app/routes/sessions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.coding_session import CodingSession, SessionStatus
from app.models.problem import Problem
from app.models.user import User
from app.schemas.coding_session import (
    CodingSessionCreate,
    CodingSessionUpdate,
    CodingSessionResponse
)
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["Coding Sessions"])


@router.post("/", response_model=CodingSessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    session_data: CodingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new coding session for a problem"""
    
    # Check if problem exists
    problem = db.query(Problem).filter(
        Problem.id == session_data.problem_id,
        Problem.is_active == True
    ).first()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Create new session
    new_session = CodingSession(
        user_id=current_user.id,
        problem_id=session_data.problem_id,
        language=session_data.language,
        current_code=getattr(problem, f"starter_code_{session_data.language}", None),
        status=SessionStatus.IN_PROGRESS
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/my", response_model=List[CodingSessionResponse])
def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all coding sessions of the current user"""
    sessions = db.query(CodingSession).filter(
        CodingSession.user_id == current_user.id
    ).order_by(CodingSession.last_activity_at.desc()).all()
    
    return sessions


@router.get("/{session_id}", response_model=CodingSessionResponse)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific coding session"""
    session = db.query(CodingSession).filter(
        CodingSession.id == session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.patch("/{session_id}", response_model=CodingSessionResponse)
def update_session(
    session_id: int,
    update_data: CodingSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current code or status of a session"""
    session = db.query(CodingSession).filter(
        CodingSession.id == session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if update_data.current_code is not None:
        session.current_code = update_data.current_code

    if update_data.status is not None:
        session.status = update_data.status
        if update_data.status == SessionStatus.COMPLETED:
            from datetime import datetime
            session.completed_at = datetime.utcnow()

    if update_data.language is not None:
        session.language = update_data.language

    db.commit()
    db.refresh(session)
    return session