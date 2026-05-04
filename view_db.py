from app.database.database import SessionLocal
from app.models import Student, User, Teacher, Admin

session = SessionLocal()

# View students
students = session.query(Student).all()
print("=== STUDENTS ===")
for student in students:
    print(f"ID: {student.id}, Name: {student.full_name}, Email: {student.email}")

# View teachers
teachers = session.query(Teacher).all()
print("\n=== TEACHERS ===")
for teacher in teachers:
    print(f"ID: {teacher.id}, Name: {teacher.full_name}, Email: {teacher.email}")

# View admins specifically using Admin class directly
try:
    admins = session.query(Admin).all()
    if admins:
        print("\n=== ADMINS ===")
        for admin in admins:
            print(f"ID: {admin.id}, Name: {admin.full_name}, Email: {admin.email}, Status: {admin.status}")
            if admin.token:
                print(f"   Token: {admin.token}")
    else:
        print("\n=== ADMINS ===")
        print("No admins found")
except Exception as e:
    print(f"\n=== ADMINS ===")
    print(f"Error: {e}")
# View all users (including admins) - use with caution if Admin records exist without Admin model
try:
    users = session.query(User).all()
    print("\n=== ALL USERS ===")
    for user in users:
        print(f"ID: {user.id}, Name: {user.full_name}, Email: {user.email}, Type: {user.type}, Status: {user.status}")
except Exception as e:
    print(f"\n=== ALL USERS ===ERROR: {e}")
    print("(This might be due to unmapped polymorphic identities)")


session.close()