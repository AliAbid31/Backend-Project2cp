from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.crud import crud_quote
from app.schemas.quotes import QuoteCreate, QuoteOut
from typing import List

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.post("/", response_model=QuoteOut)
def create_quote_endpoint(quote: QuoteCreate, db: Session = Depends(get_db)):
    """Create a new quote request"""
    return crud_quote.create_quote(db=db, quote=quote)


@router.get("/{quote_id}", response_model=QuoteOut)
def get_quote_endpoint(quote_id: int, db: Session = Depends(get_db)):
    """Get a specific quote by ID"""
    return crud_quote.get_quote(db=db, quote_id=quote_id)


@router.get("/", response_model=List[QuoteOut])
def get_quotes_endpoint(db: Session = Depends(get_db)):
    """Get all quotes"""
    return crud_quote.get_quotes(db=db)


@router.get("/student/{student_id}", response_model=List[QuoteOut])
def get_quotes_by_student_endpoint(student_id: int, db: Session = Depends(get_db)):
    """Get all quotes for a specific student"""
    return crud_quote.get_quotes_by_student(db=db, student_id=student_id)


@router.get("/teacher/{teacher_id}", response_model=List[QuoteOut])
def get_quotes_by_teacher_endpoint(teacher_id: int, db: Session = Depends(get_db)):
    """Get all quotes created by a specific teacher"""
    return crud_quote.get_quotes_by_teacher(db=db, teacher_id=teacher_id)


@router.put("/{quote_id}", response_model=QuoteOut)
def update_quote_endpoint(quote_id: int, quote_update: QuoteCreate, db: Session = Depends(get_db)):
    """Update a quote"""
    return crud_quote.update_quote(db=db, quote_id=quote_id, quote_update=quote_update)


@router.delete("/{quote_id}")
def delete_quote_endpoint(quote_id: int, db: Session = Depends(get_db)):
    """Delete a quote"""
    if crud_quote.delete_quote(db=db, quote_id=quote_id):
        return {"message": "Quote deleted successfully"}
    raise HTTPException(status_code=404, detail="Quote not found")


@router.post("/{quote_id}/accept", response_model=QuoteOut)
def accept_quote_endpoint(quote_id: int, db: Session = Depends(get_db)):
    """Accept a quote request - teacher accepts work from student"""
    return crud_quote.accept_quote(db=db, quote_id=quote_id)


@router.post("/{quote_id}/decline", response_model=QuoteOut)
def decline_quote_endpoint(quote_id: int, db: Session = Depends(get_db)):
    """Decline a quote request"""
    return crud_quote.decline_quote(db=db, quote_id=quote_id)













