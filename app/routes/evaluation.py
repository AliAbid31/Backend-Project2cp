from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.crud.crud_evaluation import (
    create_evaluation,
    get_evaluation,
    get_evaluations_for_teacher,
    get_evaluations_by_evaluator,
    get_all_evaluations
)
from app.schemas.evaluation import EvaluationCreate, EvaluationOut
from app.database.database import SessionLocal

router = APIRouter(
    prefix="/evaluations",
    tags=["evaluations"]
)




@router.post("/", response_model=EvaluationOut)
def submit_evaluation(
    evaluation: EvaluationCreate,
    
    db: Session = Depends(get_db)
):
    return create_evaluation(db, evaluation)


@router.get("/", response_model=list[EvaluationOut])
def list_all_evaluations(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_all_evaluations(db, limit)



@router.get("/teacher/{teacher_id}")
def get_teacher_evaluations(
    teacher_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_evaluations_for_teacher(db, teacher_id, limit)


@router.get("/student/{evaluator_id}", response_model=list[EvaluationOut])
def get_evaluator_ratings(
    evaluator_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_evaluations_by_evaluator(db, evaluator_id, limit)
