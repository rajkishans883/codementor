# backend/app/routes/test_cases.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.problem import Problem
from app.models.problem_test_case import ProblemTestCase
from app.schemas.test_case import TestCaseCreate, TestCaseResponse, TestCasePublicResponse
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/test-cases", tags=["Test Cases"])


@router.post("/", response_model=TestCaseResponse)
def create_test_case(
    data: TestCaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a test case for a problem (admin use for now)"""
    
    problem = db.query(Problem).filter(Problem.id == data.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    test_case = ProblemTestCase(
        problem_id=data.problem_id,
        input_data=data.input_data,
        expected_output=data.expected_output,
        is_hidden=data.is_hidden,
        order=data.order,
        explanation=data.explanation
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@router.get("/problem/{problem_id}", response_model=List[TestCasePublicResponse])
def get_visible_test_cases(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """Get only visible (non-hidden) test cases for students"""
    
    test_cases = db.query(ProblemTestCase).filter(
        ProblemTestCase.problem_id == problem_id,
        ProblemTestCase.is_hidden == False
    ).order_by(ProblemTestCase.order).all()

    return test_cases


@router.get("/problem/{problem_id}/all", response_model=List[TestCaseResponse])
def get_all_test_cases(
    problem_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all test cases including hidden ones"""
    
    test_cases = db.query(ProblemTestCase).filter(
        ProblemTestCase.problem_id == problem_id
    ).order_by(ProblemTestCase.order).all()

    return test_cases