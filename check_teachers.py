from app.database.database import SessionLocal
from app.models.teacher import Teacher

def check_teacher_details():
    db = SessionLocal()
    teachers = db.query(Teacher).all()
    print(f"{'ID':<5} | {'Subject':<10} | {'Level':<10} | {'Location Mode':<15} | {'Address':<15}")
    print("-" * 65)
    for t in teachers:
        print(f"{t.id:<5} | {str(t.subject):<10} | {str(t.teachinglevel):<10} | {str(t.location_mode):<15} | {str(t.postal_address):<15}")
    db.close()

if __name__ == "__main__":
    check_teacher_details()
