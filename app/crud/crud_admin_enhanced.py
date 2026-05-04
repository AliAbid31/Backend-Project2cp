"""
Enhanced Admin Dashboard Utilities
Provides comprehensive statistics for admin dashboard
"""

from sqlalchemy import func, or_, desc
from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.models.users import User
from app.models.students import Student
from app.models.evaluation import Evaluation
from app.models.session import Session as SessionModel
from app.models.services import Service
from app.models.quote import Quote
from app.models.parents import Parent


def get_enhanced_dashboard_stats(db: Session) -> dict:
    """
    Get comprehensive dashboard statistics including all metrics
    """
    # Basic counts
    total_teachers = db.query(User).filter(User.type == "Teacher", User.status == "active").count()
    pending_teachers = db.query(User).filter(User.type == "Teacher", User.status == "pending").count()
    total_students = db.query(Student).count()
    total_parents = db.query(Parent).count()
    total_services = db.query(Service).count()
    total_sessions = db.query(SessionModel).count()
    
    # Additional metrics
    completed_sessions = db.query(SessionModel).filter(SessionModel.status == "completed").count()
    pending_sessions = db.query(SessionModel).filter(SessionModel.status == "pending").count()
    total_evaluations = db.query(Evaluation).count()
    pending_quotes = db.query(Quote).filter(Quote.status == "pending").count()
    
    # Teachers with ratings
    teachers_with_ratings = db.query(Teacher).join(
        Evaluation, Evaluation.teacher_id == Teacher.id
    ).filter(Teacher.status == "active").distinct().count()
    
    # Average rating across all teachers
    avg_rating_overall = db.query(func.avg(Evaluation.note)).scalar() or 0
    
    return {
        "total_teachers": total_teachers,
        "pending_teachers": pending_teachers,
        "total_students": total_students,
        "total_parents": total_parents,
        "total_services": total_services,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "pending_sessions": pending_sessions,
        "total_evaluations": total_evaluations,
        "pending_quotes": pending_quotes,
        "teachers_with_ratings": teachers_with_ratings,
        "average_rating": round(float(avg_rating_overall), 2),
    }


def get_top_performing_teachers_enhanced(db: Session, limit: int = 5):
    """
    Get top performing teachers with enhanced metrics
    Includes teachers with or without evaluations
    """
    # Teachers WITH evaluations - ranked by rating
    rows_with_evaluations = (
        db.query(
            Teacher.id.label("id"),
            Teacher.full_name.label("full_name"),
            Teacher.domain.label("domain"),
            Teacher.subject.label("subject"),
            Teacher.profile_picture.label("profile_picture"),
            func.avg(Evaluation.note).label("average_rating"),
            func.count(Evaluation.id).label("evaluation_count"),
        )
        .outerjoin(Evaluation, Evaluation.teacher_id == Teacher.id)
        .filter(Teacher.status == "active")
        .group_by(
            Teacher.id,
            Teacher.full_name,
            Teacher.domain,
            Teacher.subject,
            Teacher.profile_picture,
        )
        .having(func.count(Evaluation.id) > 0)  # Only teachers with evaluations
        .order_by(
            desc(func.avg(Evaluation.note)),  # By rating
            desc(func.count(Evaluation.id))   # Then by review count
        )
        .limit(limit)
        .all()
    )
    
    result = []
    for row in rows_with_evaluations:
        teacher_id, full_name, domain, subject, profile_picture, average_rating, evaluation_count = row
        
        # Get additional stats for this teacher
        sessions_count = db.query(SessionModel).filter(SessionModel.teacher_id == teacher_id).count()
        services_count = db.query(Service).filter(Service.teacher_id == teacher_id).count()
        
        result.append({
            "id": teacher_id,
            "full_name": full_name,
            "domain": domain,
            "subject": subject,
            "profile_picture": profile_picture,
            "average_rating": round(float(average_rating or 0), 2),
            "evaluation_count": int(evaluation_count or 0),
            "sessions_count": sessions_count,
            "services_count": services_count,
            "badge": get_teacher_badge(average_rating, evaluation_count),
        })
    
    return result


def get_teacher_badge(average_rating, evaluation_count):
    """Determine the badge category for a teacher"""
    if average_rating is None:
        return "NO_RATING"
    
    rating = float(average_rating)
    count = int(evaluation_count or 0)
    
    if rating >= 4.9:
        return "TOP_RATED"
    elif count >= 20:
        return "MOST_REVIEWED"
    elif rating >= 4.5:
        return "EXCELLENT"
    elif rating >= 4.0:
        return "VERY_GOOD"
    elif rating >= 3.5:
        return "GOOD"
    else:
        return "ACCEPTABLE"


def get_dashboard_summary(db: Session) -> dict:
    """Get a quick summary for dashboard overview"""
    stats = get_enhanced_dashboard_stats(db)
    top_teachers = get_top_performing_teachers_enhanced(db, limit=3)
    
    return {
        "stats": stats,
        "top_performing_teachers": top_teachers,
    }


# Example usage in admin routes:
"""
@router.get("/dashboard/stats/enhanced")
def get_enhanced_admin_stats(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    '''Get enhanced admin dashboard statistics with more metrics'''
    return get_dashboard_summary(db)
"""
