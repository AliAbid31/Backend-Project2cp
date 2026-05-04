from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.models.users import User
from app.models.report import Report
from app.models.students import Student
from app.models.parents import Parent
from app.models.documents import Document
from app.models.quotes import Quote
from app.models.certificates import Certificate
from app.models.notifications import Notification
from app.models.messages import Messages
from app.models.email_verification import EmailVerification
from app.models.session_audit import SessionAudit
from app.models.services import Service
from app.models.session import Session
from app.models.evaluation import Evaluation
from app.models.teacher_application import TeacherApplication
from app.models.association_teacher_student import teacher_student
from app.models.association_teacher_subjects import teacher_subjects
from app.models.association_teacher_level import teacher_levels
from app.models.association_student_session import student_session
from app.models.association_student_quote import student_quote
from app.models.association_student_service import student_service
from app.models.association_student_document import student_document
from fastapi import HTTPException
from app.services import email_service
import json

def get_pending_teachers(db: Session):
    apps = (
        db.query(TeacherApplication)
        .filter(func.lower(TeacherApplication.status) == "pending")
        .order_by(TeacherApplication.id.desc())
        .all()
    )
    return [
        {
            "id": app.id,
            "full_name": app.full_name,
            "email": app.email,
            "phone_number": app.phone_number,
            "postal_address": app.postal_address,
            "geo_coordinates": app.geo_coordinates,
            "subject": app.subject,
            "teachinglevel": app.teachinglevel,
            "location_mode": app.location_mode,
            "deplacemnt": app.deplacemnt,
            "nature": app.nature,
            "domain": app.domain,
            "profile_picture": app.profile_picture,
            "bio": app.bio,
            "payment_method": app.payment_method,
            "payment_info": app.payment_info,
            "status": app.status,
        }
        for app in apps
    ]

def get_teacher_by_id(db: Session, teacher_id: int):
    app = db.query(TeacherApplication).filter(TeacherApplication.id == teacher_id).first()
    if not app:
        return None
    certs = json.loads(app.certificates_json or "[]")
    return {
        "id": app.id,
        "full_name": app.full_name,
        "email": app.email,
        "phone_number": app.phone_number,
        "postal_address": app.postal_address,
        "geo_coordinates": app.geo_coordinates,
        "subject": app.subject,
        "teachinglevel": app.teachinglevel,
        "location_mode": app.location_mode,
        "deplacemnt": app.deplacemnt,
        "nature": app.nature,
        "domain": app.domain,
        "profile_picture": app.profile_picture,
        "bio": app.bio,
        "payment_method": app.payment_method,
        "payment_info": app.payment_info,
        "status": app.status,
        "certificates": certs,
    }

def approve_teacher(db: Session, teacher_id: int, admin_notes: str = None) -> dict:
    application = db.query(TeacherApplication).filter(TeacherApplication.id == teacher_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    if (application.status or "").strip().lower() != "pending":
        raise HTTPException(status_code=400, detail=f"Teacher status is {application.status}")

    existing_user = db.query(User).filter(func.lower(User.email) == (application.email or "").strip().lower()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    teacher = Teacher(
        full_name=application.full_name,
        email=application.email,
        phone_number=application.phone_number,
        postal_address=application.postal_address,
        geo_coordinates=application.geo_coordinates,
        password=application.password,
        subject=application.subject,
        teachinglevel=application.teachinglevel,
        location_mode=application.location_mode,
        deplacemnt=application.deplacemnt,
        nature=application.nature,
        domain=application.domain,
        profile_picture=application.profile_picture,
        bio=application.bio,
        payment_method=application.payment_method,
        payment_info=application.payment_info,
        type="Teacher",
        status="active",
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    certs = json.loads(application.certificates_json or "[]")
    for cert in certs:
        db.add(
            Certificate(
                teacher_id=teacher.id,
                file_path=cert.get("file_path"),
                title=cert.get("title"),
                name=cert.get("name"),
            )
        )
    db.query(TeacherApplication).filter(TeacherApplication.id == teacher_id).delete(synchronize_session=False)
    db.commit()
    
    # Send Email
    try:
        email_service.send_teacher_approval_email(teacher.email, teacher.full_name)
    except Exception as e:
        print(f"Failed to send approval email: {e}")
    
    return {
        "success": True,
        "message": f"Teacher {teacher.full_name} approved and notified.",
        "teacher_id": teacher.id,
        "status": "active"
    }

def reject_teacher(db: Session, teacher_id: int, rejection_reason: str = None) -> dict:
    application = db.query(TeacherApplication).filter(TeacherApplication.id == teacher_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    if (application.status or "").strip().lower() != "pending":
        raise HTTPException(status_code=400, detail=f"Teacher status is {application.status}")
    
    teacher_email = application.email
    teacher_name = application.full_name

    db.query(TeacherApplication).filter(TeacherApplication.id == teacher_id).delete(synchronize_session=False)
    db.commit()

    # Send Email
    try:
        email_service.send_teacher_rejection_email(teacher_email, teacher_name, rejection_reason)
    except Exception as e:
        print(f"Failed to send rejection email: {e}")

    return {
        "success": True,
        "message": f"Teacher application for {teacher_name} rejected and notified.",
        "teacher_id": teacher_id,
        "status": "rejected"
    }

def get_all_teachers_by_status(db: Session, status_filter: str):
    normalized_status = (status_filter or "").strip().lower()
    return db.query(Teacher).filter(func.lower(Teacher.status) == normalized_status).all()

def count_pending_teachers(db: Session) -> int:
    return (
        db.query(TeacherApplication)
        .filter(func.lower(TeacherApplication.status) == "pending")
        .count()
    )

def get_dashboard_stats(db: Session) -> dict:
    # Query from the User table where type = 'Teacher'
    total_teachers = (
        db.query(User)
        .filter(func.lower(User.type) == "teacher", func.lower(User.status) == "active")
        .count()
    )
    active_teachers = total_teachers
    pending_teachers = (
        db.query(TeacherApplication)
        .filter(func.lower(TeacherApplication.status) == "pending")
        .count()
    )
    
    total_students = db.query(Student).count()
    total_parents = db.query(Parent).count()
    total_services = db.query(Service).count()
    total_sessions = db.query(Session).count()

    return {
        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "total_students": total_students,
        "total_parents": total_parents,
        "total_services": total_services,
        "total_sessions": total_sessions,
        "pending_teachers": pending_teachers,
    }

def get_all_users(db: Session):
    # Return users for admin "Users" directory:
    # - Exclude admins
    # - Show teachers only when active
    # Keep role/status checks case-insensitive to avoid mismatches from DB casing.
    return (
        db.query(User)
        .filter(
            func.lower(User.type) != "admin",
            (func.lower(User.type) != "teacher")
            | (
                (func.lower(User.type) == "teacher")
                & (func.lower(User.status) == "active")
            ),
        )
        .order_by(User.id.desc())
        .all()
    )

def get_users_by_type(db: Session, user_type: str):
    normalized_type = (user_type or "").strip().lower()
    query = db.query(User).filter(func.lower(User.type) == normalized_type)
    if normalized_type == "teacher":
        query = query.filter(func.lower(User.status) == "active")
    return query.order_by(User.id.desc()).all()

def get_users_by_status(db: Session, status_filter: str):
    normalized_status = (status_filter or "").strip().lower()
    return (
        db.query(User)
        .filter(func.lower(User.status) == normalized_status)
        .order_by(User.id.desc())
        .all()
    )

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def delete_user(db: Session, user_id: int) -> dict:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_name = user.full_name
    user_email = user.email
    user_type = user.type

    if user_type == "Teacher":
        session_ids = [row.id for row in db.query(Session.id).filter(Session.teacher_id == user_id).all()]
        service_ids = [row.id for row in db.query(Service.id).filter(Service.teacher_id == user_id).all()]
        quote_ids = [row.id for row in db.query(Quote.id).filter(Quote.teacher_id == user_id).all()]
        document_ids = [row.id for row in db.query(Document.id).filter(Document.teacher_id == user_id).all()]

        if session_ids:
            db.execute(student_session.delete().where(student_session.c.session_id.in_(session_ids)))
            db.query(SessionAudit).filter(SessionAudit.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(Evaluation).filter(Evaluation.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(Document).filter(Document.session_id.in_(session_ids)).delete(synchronize_session=False)

        if service_ids:
            db.execute(student_service.delete().where(student_service.c.service_id.in_(service_ids)))
            db.query(Document).filter(Document.service_id.in_(service_ids)).delete(synchronize_session=False)

        if quote_ids:
            db.execute(student_quote.delete().where(student_quote.c.quote_id.in_(quote_ids)))

        if document_ids:
            db.execute(student_document.delete().where(student_document.c.document_id.in_(document_ids)))

        db.execute(teacher_student.delete().where(teacher_student.c.teacher_id == user_id))
        db.execute(teacher_subjects.delete().where(teacher_subjects.c.teacher_id == user_id))
        db.execute(teacher_levels.delete().where(teacher_levels.c.teacher_id == user_id))

        db.query(Report).filter(or_(Report.teacher_id == user_id, Report.reporter_id == user_id)).delete(synchronize_session=False)
        db.query(Evaluation).filter(or_(Evaluation.teacher_id == user_id, Evaluation.evaluator_id == user_id)).delete(synchronize_session=False)
        db.query(Document).filter(Document.teacher_id == user_id).delete(synchronize_session=False)
        db.query(Session).filter(Session.teacher_id == user_id).delete(synchronize_session=False)
        db.query(Service).filter(Service.teacher_id == user_id).delete(synchronize_session=False)
        db.query(Quote).filter(Quote.teacher_id == user_id).delete(synchronize_session=False)
        db.query(Certificate).filter(Certificate.teacher_id == user_id).delete(synchronize_session=False)

    elif user_type == "Student":
        db.execute(teacher_student.delete().where(teacher_student.c.student_id == user_id))
        db.execute(student_quote.delete().where(student_quote.c.student_id == user_id))
        db.execute(student_service.delete().where(student_service.c.student_id == user_id))
        db.execute(student_session.delete().where(student_session.c.student_id == user_id))
        db.execute(student_document.delete().where(student_document.c.student_id == user_id))

        db.query(Report).filter(or_(Report.student_id == user_id, Report.reporter_id == user_id)).delete(synchronize_session=False)
        db.query(Evaluation).filter(Evaluation.evaluator_id == user_id).delete(synchronize_session=False)

    db.query(Notification).filter(Notification.user_id == user_id).delete(synchronize_session=False)
    db.query(Messages).filter(or_(Messages.sender_id == user_id, Messages.receiver_id == user_id)).delete(synchronize_session=False)
    db.query(EmailVerification).filter(EmailVerification.user_id == user_id).delete(synchronize_session=False)

    if user_type == "Teacher":
        db.query(Teacher).filter(Teacher.id == user_id).delete(synchronize_session=False)
    elif user_type == "Student":
        db.query(Student).filter(Student.id == user_id).delete(synchronize_session=False)

    db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()

    return {
        "success": True,
        "message": f"User {user_name} deleted successfully",
        "user_id": user_id,
        "user_email": user_email,
        "user_type": user_type,
    }

def ban_user(db: Session, user_id: int) -> dict:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "banned"
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": f"User {user.email} has been banned",
        "user_id": user.id,
        "user_email": user.email,
        "user_type": user.type,
    }

def unban_user(db: Session, user_id: int) -> dict:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "active"
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": f"User {user.email} has been unbanned",
        "user_id": user.id,
        "new_status": user.status,
    }

def get_all_users_by_type(db: Session, user_type: str):
    return get_users_by_type(db, user_type)

def get_top_performing_teachers(db: Session, limit: int = 3):
    rows = (
        db.query(
            Teacher.id.label("id"),
            Teacher.full_name.label("full_name"),
            Teacher.domain.label("domain"),
            Teacher.subject.label("subject"),
            Teacher.profile_picture.label("profile_picture"),
            func.avg(Evaluation.note).label("average_rating"),
            func.count(Evaluation.id).label("evaluation_count"),
        )
        .join(Evaluation, Evaluation.teacher_id == Teacher.id)
        .filter(func.lower(Teacher.status) == "active")
        .group_by(
            Teacher.id,
            Teacher.full_name,
            Teacher.domain,
            Teacher.subject,
            Teacher.profile_picture,
        )
        .order_by(func.avg(Evaluation.note).desc(), func.count(Evaluation.id).desc())
        .limit(limit)
        .all()
    )

    result = []
    for teacher_id, full_name, domain, subject, profile_picture, average_rating, evaluation_count in rows:
        result.append({
            "id": teacher_id,
            "full_name": full_name,
            "domain": domain,
            "subject": subject,
            "profile_picture": profile_picture,
            "average_rating": round(float(average_rating or 0), 2),
            "evaluation_count": int(evaluation_count or 0),
        })

    return result

def get_all_reports(db: Session):
    return db.query(Report).all()

def get_reports_by_type(db: Session, report_type: str):
    return db.query(Report).filter(Report.report_type == report_type).all()

def delete_report(db: Session, report_id: int) -> dict:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()

    return {
        "success": True,
        "message": "Report deleted",
        "report_id": report_id,
    }

def ignore_report(db: Session, report_id: int) -> dict:
    return delete_report(db, report_id)

def suspend_report(db: Session, report_id: int) -> dict:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    reported_user_id = report.teacher_id or report.student_id
    if reported_user_id:
        try:
            ban_user(db, reported_user_id)
        except HTTPException:
            pass

        try:
            delete_user(db, reported_user_id)
        except HTTPException:
            pass

    remaining = db.query(Report).filter(Report.id == report_id).first()
    if remaining:
        db.delete(remaining)
        db.commit()

    return {
        "success": True,
        "message": "Report resolved and user suspended",
        "report_id": report_id,
        "reported_user_id": reported_user_id,
    }

def build_report_summary(db: Session, report: Report) -> dict:
    reporter = report.reporter or db.query(User).filter(User.id == report.reporter_id).first()
    reported_user_id = report.teacher_id if report.report_type == "teacher" else report.student_id
    reported_user = None
    if reported_user_id:
        reported_user = db.query(User).filter(User.id == reported_user_id).first()

    reporter_avatar = None
    if reporter and reporter.type == "Teacher":
        reporter_avatar = db.query(Teacher).filter(Teacher.id == reporter.id).first()
        reporter_avatar = reporter_avatar.profile_picture if reporter_avatar else None

    return {
        "id": report.id,
        "reason": report.reason,
        "description": report.description,
        "report_type": report.report_type,
        "reporter": {
            "id": reporter.id if reporter else None,
            "full_name": reporter.full_name if reporter else "Unknown Reporter",
            "email": reporter.email if reporter else None,
            "type": reporter.type if reporter else None,
            "profile_picture": reporter_avatar,
        },
        "reported_user": {
            "id": reported_user.id if reported_user else None,
            "full_name": reported_user.full_name if reported_user else "Unknown User",
            "email": reported_user.email if reported_user else None,
            "type": reported_user.type if reported_user else report.report_type,
        },
    }

def get_all_reports_with_users(db: Session):
    reports = get_all_reports(db)
    return [build_report_summary(db, report) for report in reports]

def get_reports_by_type_with_users(db: Session, report_type: str):
    reports = get_reports_by_type(db, report_type)
    return [build_report_summary(db, report) for report in reports]
