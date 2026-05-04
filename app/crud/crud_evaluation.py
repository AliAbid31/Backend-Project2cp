from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.evaluation import Evaluation
from app.models.report import Report
from app.models.teacher import Teacher
from app.models.students import Student
from app.models.users import User
from app.schemas.evaluation import EvaluationCreate, EvaluationOut
from fastapi import HTTPException
from app.models.session import Session as SessionModel





def create_evaluation(db: Session, evaluation: EvaluationCreate):
    
    # Simple check for now to allow easier testing as requested
    db_evaluation = Evaluation(
        comment=evaluation.comment,
        date=evaluation.date,
        note=evaluation.note,
        teacher_id=evaluation.teacher_id,
        evaluator_id=evaluation.evaluator_id,
        session_id=evaluation.session_id
    )
    
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def get_evaluation(db: Session, evaluation_id: int) -> EvaluationOut:
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    has_report = _has_reports(db, evaluation.evaluator_id)
    
    return EvaluationOut(
        id=evaluation.id,
        comment=evaluation.comment,
        date=evaluation.date,
        note=evaluation.note,
        teacher_id=evaluation.teacher_id,
        evaluator_id=evaluation.evaluator_id,
        session_id=evaluation.session_id,
        has_report_on_evaluator=has_report
    )


def get_evaluations_for_teacher(db: Session, teacher_id: int, limit: int = 100):
    
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    evaluations = db.query(Evaluation).filter(
        Evaluation.teacher_id == teacher_id
    ).limit(limit).all()
    
    result = []
    for evaluation in evaluations:
        student_user = db.query(User).filter(User.id == evaluation.evaluator_id).first()
        student_model = db.query(Student).filter(Student.id == evaluation.evaluator_id).first()
        
        result.append({
            "id": evaluation.id,
            "comment": evaluation.comment,
            "date": evaluation.date,
            "note": evaluation.note,
            "rating": evaluation.note,  # Add alias for frontend expect 'rating'
            "teacher_id": evaluation.teacher_id,
            "evaluator_id": evaluation.evaluator_id,
            "session_id": evaluation.session_id,
            "student_name": student_user.full_name if student_user else "Unknown Student",
            "student_avatar": None # Placeholder for avatar
        })
    
    return result


def get_evaluations_by_evaluator(db: Session, evaluator_id: int, limit: int = 100):
    
    evaluator = db.query(User).filter(User.id == evaluator_id).first()
    if not evaluator:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    
    evaluations = db.query(Evaluation).filter(
        Evaluation.evaluator_id == evaluator_id
    ).limit(limit).all()
    
    result = []
    for evaluation in evaluations:
        has_report = _has_reports(db, evaluator_id)
        result.append(EvaluationOut(
            id=evaluation.id,
            comment=evaluation.comment,
            date=evaluation.date,
            note=evaluation.note,
            teacher_id=evaluation.teacher_id,
            evaluator_id=evaluation.evaluator_id,
            session_id=evaluation.session_id,
            has_report_on_evaluator=has_report
        ))
    
    return result


def get_all_evaluations(db: Session, limit: int = 100):
    evaluations = db.query(Evaluation).limit(limit).all()
    
    result = []
    for evaluation in evaluations:
        has_report = _has_reports(db, evaluation.evaluator_id)
        result.append(EvaluationOut(
            id=evaluation.id,
            comment=evaluation.comment,
            date=evaluation.date,
            note=evaluation.note,
            teacher_id=evaluation.teacher_id,
            evaluator_id=evaluation.evaluator_id,
            session_id=evaluation.session_id,
            has_report_on_evaluator=has_report
        ))
    
    return result


def _has_reports(db: Session, student_id: int) -> bool:
    report = db.query(Report).filter(
        and_(
            Report.report_type == "student",
            Report.student_id == student_id
        )
    ).first()
    return report is not None
