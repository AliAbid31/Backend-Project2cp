from fastapi import APIRouter, Depends, HTTPException,FastAPI

from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.users import User
from app.models.parents import Parent
from app.crud.crud_parents import create_parent, get_parent, get_parents, delete_parent, delete_all_parents, add_child_to_parent
from typing import List
from app.schemas.parents import ParentCreate, ParentOut
from app.schemas.students import ChildProfileCreate, ChildProfileOut
router = APIRouter(
    prefix="/parents",
    tags=["parents"],
)

@router.post("/", response_model=ParentOut)
def create_parent_endpoint(parent: ParentCreate, db: Session = Depends(get_db)):
  return create_parent(db, parent)

@router.post("/{parent_id}/children", response_model=ChildProfileOut)
def add_child_to_parent_endpoint(parent_id: int, child: ChildProfileCreate, db: Session = Depends(get_db)):
  return add_child_to_parent(db, parent_id, child)

@router.get("/{parent_id}", response_model=ParentOut)
def get_parent_endpoint(parent_id: int, db: Session = Depends(get_db)):
  return get_parent(db, parent_id)

@router.delete("/{parent_username}")
def delete_parent_endpoint(parent_username: str, parent_password: str, db: Session = Depends(get_db)):
  if delete_parent(db, parent_username, parent_password):
    return {"message": "Parent deleted successfully"}
  raise HTTPException(status_code=404, detail="Parent not found")

@router.get("/", response_model=List[ParentOut])
def get_parents_endpoint(db: Session = Depends(get_db)):
  return get_parents(db)

@router.delete("/")
def delete_all_parents_endpoint(db: Session = Depends(get_db)):
  delete_all_parents(db)
  return {"message": "All parents deleted successfully"}