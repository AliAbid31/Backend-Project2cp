from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.crud import crud_admin
from app.schemas.teacher import TeacherOut
# Use the same auth dependency as the mobile/web app login flow (/api/auth/login).
from app.routes.auth import get_current_user
from app.models.users import User
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that the current user is an admin"""
    if (current_user.type or "").strip().lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access admin endpoints"
        )
    return current_user

class TeacherApprovalRequest(BaseModel):
    """Request to approve or reject a teacher"""
    admin_notes: str = None

class TeacherRejectionRequest(BaseModel):
    """Request to reject a teacher"""
    rejection_reason: str = None

class ReportResolutionRequest(BaseModel):
    """Request to resolve a report"""
    admin_notes: str = None
    ban_user: bool = False  # Whether to ban the reported user

class PendingTeacherResponse(BaseModel):
    """Response with teacher pending list"""
    total_pending: int
    teachers: List[dict]

@router.get("/teachers/pending", response_model=PendingTeacherResponse)
def get_pending_teachers(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get all teachers with pending status waiting for admin approval.
    
    Returns list of teachers that need verification:
    - Certificates
    - Academic Background
    - Expertise Domain
    - Teaching Experience
    """
    teachers = crud_admin.get_pending_teachers(db)
    return {
        "total_pending": len(teachers),
        "teachers": teachers
    }

@router.get("/teachers/pending/count")
def count_pending_teachers(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Get count of pending teachers"""
    count = crud_admin.count_pending_teachers(db)
    return {
        "pending_count": count
    }

@router.get("/teachers/status/{status_filter}")
def get_teachers_by_status(status_filter: str, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get all teachers by status.
    
    - **status_filter**: "active", "pending", or "rejected"
    """
    return crud_admin.get_all_teachers_by_status(db, status_filter)

@router.post("/teachers/{teacher_id}/approve", response_model=dict)
def approve_teacher(teacher_id: int, request: TeacherApprovalRequest, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Approve a pending teacher account.
    
    After approval:
    - Teacher can login
    - Teacher can create sessions
    - Teacher profile is visible to students
    
    Admin should verify:
    - ✅ Certificates are valid
    - ✅ Academic background is legitimate
    - ✅ Teaching experience is verifiable
    - ✅ Phone number is verified
    """
    return crud_admin.approve_teacher(db, teacher_id, request.admin_notes)

@router.post("/teachers/{teacher_id}/reject", response_model=dict)
def reject_teacher(teacher_id: int, request: TeacherRejectionRequest, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Reject a pending teacher account.
    
    After rejection:
    - Teacher cannot login
    - Teacher must reapply with corrected information
    
    Common rejection reasons:
    - Invalid certificates
    - Cannot verify academic background
    - Suspicious account activity
    - Information does not match
    """
    return crud_admin.reject_teacher(db, teacher_id, request.rejection_reason)

@router.get("/teachers/{teacher_id}")
def get_teacher_details(teacher_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Get detailed information about a specific teacher"""
    teacher = crud_admin.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.get("/dashboard/stats")
def get_admin_stats(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    stats = crud_admin.get_dashboard_stats(db)
    top_teachers = crud_admin.get_top_performing_teachers(db, limit=3)

    return {
        "stats": stats,
        "top_performing_teachers": top_teachers,
    }

@router.get("/reports")
def get_all_reports(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get all reports submitted by users.
    
    Reports include:
    - Complaints about teachers
    - Issues with sessions
    - Evaluation disputes
    - General platform issues
    """
    reports = crud_admin.get_all_reports_with_users(db)
    return {
        "total_reports": len(reports),
        "reports": reports
    }


@router.get("/reports/type/{report_type}")
def get_reports_by_type(report_type: str, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get reports filtered by type.
    
    Common report types:
    - teacher_complaint
    - student_complaint
    - evaluation_dispute
    - content_issue
    - other
    """
    reports = crud_admin.get_reports_by_type_with_users(db, report_type)
    return {
        "type": report_type,
        "total": len(reports),
        "reports": reports
    }


@router.get("/reports/{report_id}")
def get_report_details(report_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Get detailed information about a specific report"""
    report = crud_admin.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.delete("/reports/{report_id}", response_model=dict)
def delete_report(report_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Delete a report (ignore action)."""
    return crud_admin.delete_report(db, report_id)

@router.post("/reports/{report_id}/ignore", response_model=dict)
def ignore_report(report_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Ignore a report without taking action on the user."""
    return crud_admin.ignore_report(db, report_id)

@router.post("/reports/{report_id}/suspend", response_model=dict)
def suspend_report(report_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Suspend the reported user and remove the report."""
    return crud_admin.suspend_report(db, report_id)


@router.post("/reports/{report_id}/resolve")
def resolve_report(report_id: int, request: ReportResolutionRequest, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Resolve and archive a report.
    
    Admin can:
    - Review the report details
    - Decide to ban the reported user (if misconduct confirmed)
    - Or just archive without action
    - Add admin notes explaining resolution
    
    **Request Parameters:**
    - `admin_notes`: Notes explaining the decision
    - `ban_user`: Set to true to ban the reported user (they will not be able to login)
    
    **Example Ban Request:**
    ```json
    {
      "admin_notes": "Confirmed inappropriate behavior, banning user",
      "ban_user": true
    }
    ```
    
    **Example Archive Only:**
    ```json
    {
      "admin_notes": "Reviewed and resolved",
      "ban_user": false
    }
    ```
    """
    report = crud_admin.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    reported_user_id = report.teacher_id or report.student_id
    
    return crud_admin.resolve_report(
        db, 
        report_id, 
        request.admin_notes,
        ban_user=request.ban_user,
        reported_user_id=reported_user_id
    )

@router.post("/users/{user_id}/ban", response_model=dict)
def ban_user(user_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Ban a user by setting status to banned."""
    return crud_admin.ban_user(db, user_id)

@router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Delete a user from the system."""
    return crud_admin.delete_user(db, user_id)

@router.get("/users")
def get_all_users(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get all users in the system.
    
    Returns all users regardless of type:
    - Students
    - Teachers
    - Parents
    - Admins
    """
    users = crud_admin.get_all_users(db)
    return {
        "total_users": len(users),
        "users": users
    }


@router.get("/users/type/{user_type}")
def get_users_by_type(user_type: str, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get all users of a specific type.
    
    Valid user types:
    - Student
    - Teacher
    - Parent
    - Admin
    """
    users = crud_admin.get_users_by_type(db, user_type)
    return {
        "type": user_type,
        "total": len(users),
        "users": users
    }


@router.get("/users/status/{status_filter}")
def get_users_by_status(status_filter: str, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get all users with a specific status.
    
    Valid statuses:
    - active: Account is active and can login
    - pending: Account waiting for approval (Teachers)
    - rejected: Account has been rejected
    """
    users = crud_admin.get_users_by_status(db, status_filter)
    return {
        "status": status_filter,
        "total": len(users),
        "users": users
    }


@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Get a single user by ID for the admin users directory.
    """
    try:
        user = crud_admin.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Build dictionary manually to include all fields without a strict Pydantic model
        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "postal_address": user.postal_address,
            "type": user.type,
            "status": getattr(user, "status", "active"),
            "created_at": getattr(user, "created_at", None),
            "profile_picture": getattr(user, "profile_picture", None),
            "subject": getattr(user, "subject", None),
            "teachinglevel": getattr(user, "teachinglevel", None)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Remove/delete a user from the system.
    
    ⚠️ WARNING: This is a destructive action!
    
    This will permanently delete:
    - User account
    - All messages and communications
    - Reports submitted by the user
    - Sessions (if applicable)
    - Evaluation history
    - All related data
    
    Common reasons to delete users:
    - Account abuse or policy violations
    - Spam/bot accounts
    - Duplicate accounts
    - User requested deletion
    - Banned user cleanup
    
    Args:
        user_id: ID of user to delete
    """
    return crud_admin.delete_user(db, user_id)


@router.post("/users/{user_id}/ban")
def ban_user(user_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Ban a user from the platform.
    
    ⚠️ Banned users CANNOT login or access the platform.
    
    Use this when:
    - User behavior violates platform policies
    - User is reported multiple times for misconduct
    - User engaged in harassment or abuse
    - User violated terms of service
    
    **Effect:**
    - User status set to "banned"
    - User cannot login (will get 403 Forbidden)
    - All user data remains in database
    - Can be unbanned later if needed
    
    Args:
        user_id: ID of user to ban
    
    Example response:
    ```json
    {
      "success": true,
      "message": "User john@example.com has been banned",
      "user_id": 5,
      "user_email": "john@example.com",
      "user_type": "Teacher"
    }
    ```
    """
    return crud_admin.ban_user(db, user_id)


@router.post("/users/{user_id}/unban")
def unban_user(user_id: int, admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """
    Unban a user to allow them to login again.
    
    Use this when:
    - Ban period is over
    - User behavior has improved
    - Ban was accidental or mistaken
    
    **Effect:**
    - User status set to "active"
    - User can login again normally
    - User regains full platform access
    
    Args:
        user_id: ID of user to unban
    
    Example response:
    ```json
    {
      "success": true,
      "message": "User john@example.com has been unbanned",
      "user_id": 5,
      "user_email": "john@example.com",
      "new_status": "active"
    }
    ```
    """
    return crud_admin.unban_user(db, user_id)
