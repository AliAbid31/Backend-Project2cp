from app.database.database import SessionLocal
from app.models.admin import Admin
import secrets

def create_admin_user():
    """Create an admin user for testing"""
    db = SessionLocal()
    
    admin_email = "sersaabdo@gmail.com"
    admin_password = "hani2006"
    
    # Check if admin already exists
    existing = db.query(Admin).filter(Admin.email == admin_email).first()
    if existing:
        print(f"✅ Admin already exists: {admin_email}")
        print(f"Token: {existing.token}")
        print(f"Type: {existing.type}")
        db.close()
        return
    
    # Create new admin with token using Admin model directly
    token = secrets.token_hex(32)
    admin = Admin(
        full_name="Admin User",
        email=admin_email,
        password=admin_password,
        status="active",
        token=token,
        phone_number="1234567890",
        admin_level="super"
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("=" * 60)
    print("✅ ADMIN USER CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Email:    {admin_email}")
    print(f"Password: {admin_password}")
    print(f"Type:     {admin.type}")
    print(f"Token:    {token}")
    print("=" * 60)
    print("\nUse this token in requests:")
    print(f'curl -H "Authorization: Bearer {token}" \\')
    print(f'  http://localhost:8000/api/admin/teachers/pending')
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    create_admin_user()
