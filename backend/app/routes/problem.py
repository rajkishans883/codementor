from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.problem import Problem, Difficulty, ProblemType
from app.schemas.problem import ProblemResponse, ProblemListResponse

router= APIRouter(prefix="/api/problems",tags=["Problems"])

@router.get("/",response_model=List[ProblemListResponse],status_code=200)
def get_problems(
    difficulty: Optional[Difficulty] = None,
    problem_type: Optional[ProblemType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of problems with optional filters"""
    query=db.query(Problem).filter(Problem.is_active==True)

    if difficulty:
        query=query.filter(Problem.difficulty==difficulty)
    if problem_type:
        query=query.filter(Problem.problem_type==problem_type)

    problems=query.offset(skip).limit(limit).all()
    return problems

@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem_by_id(problem_id: int, db: Session = Depends(get_db)):
    """Get a single problem by ID"""
    problem = db.query(Problem).filter(
        Problem.id == problem_id,
        Problem.is_active == True
    ).first()

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    return problem

@router.get("/slug/{slug}", response_model=ProblemResponse)
def get_problem_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a single problem by slug"""
    problem = db.query(Problem).filter(
        Problem.slug == slug,
        Problem.is_active == True
    ).first()

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    return problem