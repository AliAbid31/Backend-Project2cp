from sqlalchemy.orm import Session
from app.models.report import Report
from app.models.evaluation import Evaluation
from app.models.users import User
from app.models.teacher import Teacher
from app.models.students import Student
from app.models.session import Session as SessionModel
from app.schemas.report import ReportType
from fastapi import HTTPException


# ============ INDEPENDENT REPORTING FUNCTIONS ============

def student_report_student(db: Session, evaluation_id: int, reporter_id: int, reason: str, description: str, screenshot_path: str = None):
    """Student reports another student via evaluation comment"""
    # Verify reporter is a student
    reporter = db.query(User).filter(User.id == reporter_id).first()
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    
    if reporter.type.strip().capitalize() != "Student":
        raise HTTPException(status_code=403, detail="Only students can use this endpoint")
    
    # Verify evaluation exists and has a valid comment
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    if not evaluation.comment or not evaluation.comment.strip():
        raise HTTPException(status_code=400, detail="You can only report evaluations with text comments")
    
    # Create report
    db_report = Report(
        report_type=ReportType.STUDENT.value,
        description=description,
        reason=reason,
        screenshot_path=screenshot_path,
        reporter_id=reporter_id,
        teacher_id=evaluation.teacher_id,
        student_id=evaluation.evaluator_id,
        evaluation_id=evaluation_id
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def student_report_teacher(db: Session, teacher_id: int, reporter_id: int, reason: str, description: str, screenshot_path: str = None):
    """Student reports a teacher they had a session with"""
    # Verify reporter is a student
    reporter = db.query(User).filter(User.id == reporter_id).first()
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    
    if reporter.type.strip().capitalize() != "Student":
        raise HTTPException(status_code=403, detail="Only students can use this endpoint")
    
    # Verify teacher exists
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Create report
    db_report = Report(
        report_type=ReportType.TEACHER.value,
        description=description,
        reason=reason,
        screenshot_path=screenshot_path,
        reporter_id=reporter_id,
        teacher_id=teacher_id,
        student_id=reporter_id
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def teacher_report_student(db: Session, evaluation_id: int, reporter_id: int, reason: str, description: str, screenshot_path: str = None):
    """Teacher reports a student via evaluation comment"""
    # Verify reporter is a teacher
    reporter = db.query(User).filter(User.id == reporter_id).first()
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    
    if reporter.type.strip().capitalize() != "Teacher":
        raise HTTPException(status_code=403, detail="Only teachers can use this endpoint")
    
    # Verify evaluation exists and has a valid comment
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    if not evaluation.comment or not evaluation.comment.strip():
        raise HTTPException(status_code=400, detail="You can only report evaluations with text comments")
    
    # Create report
    db_report = Report(
        report_type=ReportType.STUDENT.value,
        description=description,
        reason=reason,
        screenshot_path=screenshot_path,
        reporter_id=reporter_id,
        teacher_id=evaluation.teacher_id,
        student_id=evaluation.evaluator_id,
        evaluation_id=evaluation_id
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


# ============ GET REPORTS FUNCTIONS ============

def get_all_reports(db: Session, limit: int = 100):
    """Get all reports"""
    return db.query(Report).limit(limit).all()


def get_report_by_id(db: Session, report_id: int):
    """Get a specific report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
