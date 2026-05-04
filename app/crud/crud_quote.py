from sqlalchemy.orm import Session
from app.models.quotes import Quote
from app.models.students import Student
from app.schemas.quotes import QuoteCreate
from fastapi import HTTPException


def create_quote(db: Session, quote: QuoteCreate):
   
    try:
        db_quote = Quote(
            objectif=quote.objectif,
            frequence=quote.frequence,
            duration=quote.duration,
            budget=quote.budget,
            subject=quote.subject,
            level=quote.level,
            teacher_id=quote.teacher_id,
            status="pending"
        )
        
        if quote.student_id:
            student = db.query(Student).filter(Student.id == quote.student_id).first()
            if student:
                db_quote.students.append(student)

        db.add(db_quote)
        db.commit()
        db.refresh(db_quote)
        
        # Create notification for teacher
        try:
            from app.models.notifications import Notification
            from app.models.teacher import Teacher
            from app.models.users import User
            
            teacher = db.query(Teacher).filter(Teacher.id == quote.teacher_id).first()
            if teacher:
                student_name = f"Student #{quote.student_id}" if quote.student_id else "Someone"
                if quote.student_id:
                    student = db.query(Student).filter(Student.id == quote.student_id).first()
                    if student and hasattr(student, 'user') and hasattr(student.user, 'full_name'):
                        student_name = student.user.full_name
                
                notification = Notification(
                    user_id=teacher.id,
                    message=f"📝 {student_name} requested a quote for {quote.subject} ({quote.level})",
                    notification_type="quote"
                )
                db.add(notification)
                db.commit()
        except Exception as notif_error:
            print(f"Warning: Failed to create notification: {notif_error}")
            # Don't fail the quote creation if notification fails
        
        return db_quote
    except Exception as e:
        db.rollback()
        print(f"Database Error during quote creation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create quote: {str(e)}")


def get_quote(db: Session, quote_id: int):
   
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote


def get_quotes(db: Session):
   
    return db.query(Quote).all()


def get_quotes_by_student(db: Session, student_id: int):
    
    from app.models.students import Student
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.quotes


def get_quotes_by_teacher(db: Session, teacher_id: int):
    
    quotes = db.query(Quote).filter(Quote.teacher_id == teacher_id).all()
    return quotes


def update_quote(db: Session, quote_id: int, quote_update: QuoteCreate):
    
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote.objectif = quote_update.objectif
    quote.frequence = quote_update.frequence
    quote.duration = quote_update.duration
    quote.budget = quote_update.budget
    quote.subject = quote_update.subject
    quote.level = quote_update.level
    quote.teacher_id = quote_update.teacher_id
    
    db.commit()
    db.refresh(quote)
    return quote


def delete_quote(db: Session, quote_id: int):
    """Delete a quote"""
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        return False
    db.delete(quote)
    db.commit()
    return True


def accept_quote(db: Session, quote_id: int):
    """Accept a quote - changes status to accepted"""
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    try:
        quote.status = "accepted"
        db.commit()
        db.refresh(quote)
        
        # Create notification for students
        try:
            from app.models.notifications import Notification
            if quote.students:
                for student in quote.students:
                    # Get the user_id from the student's relationship
                    student_user_id = student.user_id if hasattr(student, 'user_id') else student.id
                    
                    notification = Notification(
                        user_id=student_user_id,
                        message=f"✅ Your quote for {quote.subject} has been accepted!",
                        notification_type="quote_accepted"
                    )
                    db.add(notification)
            db.commit()
        except Exception as notif_error:
            print(f"Warning: Failed to create notification: {notif_error}")
            # Don't fail quote acceptance if notification fails
        
        return quote
    except Exception as e:
        db.rollback()
        print(f"Error accepting quote: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to accept quote: {str(e)}")


def decline_quote(db: Session, quote_id: int):
    """Decline a quote - changes status to declined"""
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    try:
        quote.status = "declined"
        db.commit()
        db.refresh(quote)
        
        # Create notification for students
        try:
            from app.models.notifications import Notification
            if quote.students:
                for student in quote.students:
                    # Get the user_id from the student's relationship
                    student_user_id = student.user_id if hasattr(student, 'user_id') else student.id
                    
                    notification = Notification(
                        user_id=student_user_id,
                        message=f"❌ Your quote for {quote.subject} has been declined.",
                        notification_type="quote_declined"
                    )
                    db.add(notification)
            db.commit()
        except Exception as notif_error:
            print(f"Warning: Failed to create notification: {notif_error}")
            # Don't fail quote decline if notification fails
        
        return quote
    except Exception as e:
        db.rollback()
        print(f"Error declining quote: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to decline quote: {str(e)}")