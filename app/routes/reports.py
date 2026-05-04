from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.crud.crud_reports import (
    student_report_student,
    student_report_teacher,
    teacher_report_student,
    get_all_reports,
    get_report_by_id
)
from app.database.database import get_db
from app.schemas.report import (
    Report, 
    StudentReportStudentRequest,
    StudentReportTeacherRequest,
    TeacherReportStudentRequest
)
from app.routes.auth import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)


@router.post("/student/report-student", response_model=Report)
def student_report_student_endpoint(
    request: StudentReportStudentRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Student reports another student via evaluation comment
    - Requires: evaluation_id, reason, description
    - Optional: screenshot_path
    - Current user must be a student
    """
    return student_report_student(
        db=db,
        evaluation_id=request.evaluation_id,
        reporter_id=current_user.id,
        reason=request.reason,
        description=request.description,
        screenshot_path=request.screenshot_path
    )


@router.post("/student/report-teacher", response_model=Report)
def student_report_teacher_endpoint(
    request: StudentReportTeacherRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Student reports a teacher they had a session with
    - Requires: teacher_id, reason, description
    - Optional: screenshot_path
    - Current user must be a student who attended a session with the teacher
    """
    return student_report_teacher(
        db=db,
        teacher_id=request.teacher_id,
        reporter_id=current_user.id,
        reason=request.reason,
        description=request.description,
        screenshot_path=request.screenshot_path
    )


@router.post("/teacher/report-student", response_model=Report)
def teacher_report_student_endpoint(
    request: TeacherReportStudentRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Teacher reports a student via evaluation comment
    - Requires: evaluation_id, reason, description
    - Optional: screenshot_path
    - Current user must be a teacher
    """
    return teacher_report_student(
        db=db,
        evaluation_id=request.evaluation_id,
        reporter_id=current_user.id,
        reason=request.reason,
        description=request.description,
        screenshot_path=request.screenshot_path
    )


@router.get("/", response_model=list[Report])
def list_all_reports(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all reports with optional limit"""
    return get_all_reports(db, limit)


@router.get("/{report_id}", response_model=Report)
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific report by ID"""
    return get_report_by_id(db, report_id)
