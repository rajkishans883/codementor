# backend/app/routes/submissions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.coding_session import CodingSession
from app.models.submission import Submission, SubmissionStatus
from app.models.problem_test_case import ProblemTestCase
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionSummaryResponse
)
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/submissions", tags=["Submissions"])


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(
    data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new code submission (Run Code)"""

    # 1. Validate coding session
    session = db.query(CodingSession).filter(
        CodingSession.id == data.coding_session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Coding session not found")

    # 2. Count total test cases for this problem
    total_test_cases = db.query(ProblemTestCase).filter(
        ProblemTestCase.problem_id == session.problem_id
    ).count()

    # 3. Create submission
    submission = Submission(
        coding_session_id=session.id,
        user_id=current_user.id,
        problem_id=session.problem_id,
        code=data.code,
        language=data.language,
        status=SubmissionStatus.PENDING,
        total_count=total_test_cases,
        passed_count=0
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    # 4. Also update the session's current_code
    session.current_code = data.code
    session.language = data.language
    db.commit()

    # Trigger code execution
    from app.services.execution_service import execution_service
    submission = execution_service.execute_submission(submission, db)

    return submission


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific submission with test results"""

    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.user_id == current_user.id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.get("/session/{session_id}", response_model=List[SubmissionSummaryResponse])
def get_session_submissions(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all submissions for a coding session"""

    session = db.query(CodingSession).filter(
        CodingSession.id == session_id,
        CodingSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    submissions = db.query(Submission).filter(
        Submission.coding_session_id == session_id
    ).order_by(Submission.created_at.desc()).all()

    return submissions


@router.get("/my", response_model=List[SubmissionSummaryResponse])
def get_my_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all submissions of the current user"""

    submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).order_by(Submission.created_at.desc()).limit(50).all()

    return submissions