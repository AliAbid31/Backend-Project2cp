from dotenv import load_dotenv

load_dotenv()


import os
import sys

# Allow running from the app directory (e.g., uvicorn main:app --reload)
# while keeping absolute imports like `from app...` working.
if os.path.basename(os.getcwd()) == "app":
  parent_dir = os.path.dirname(os.getcwd())
  if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from dotenv import load_dotenv

load_dotenv()

from app.database.database import engine, Base
from app.database.database import SessionLocal
from sqlalchemy import inspect, text
from app.models.users import User
from app.models.teacher import Teacher
from app.models.students import Student
from app.models.parents import Parent
from app.models.session import Session
from app.models.services import Service
from app.models.quotes import Quote
from app.models.evaluation import Evaluation
from app.models.documents import Document
from app.models.certificates import Certificate
from app.models.subject import Subject
from app.models.teaching_level import TeachingLevel
from app.models.teacher_application import TeacherApplication
from app.models.report import Report
from app.models.messages import Messages
from app.models.notifications import Notification
from app.models.session_audit import SessionAudit
from app.models.password_reset import PasswordReset
from app.models.email_verification import EmailVerification
from app.models.messages import Messages
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from app.routes import students, teachers, parents, users, reports, evaluation, documents, session, quotes, services, messages, notifications, email_verification, admin, auth, autth1, chatbot
from app.schemas.users import UserCreate
from app.schemas.messages import MessageBase, MessageOut
from app.services.email_service import log_email_status

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.association_student_document import student_document
from app.models.association_teacher_student import teacher_student
from app.models.association_student_service import student_service
from app.models.association_student_session import student_session
from app.models.association_student_quote import student_quote
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter, rate_limit_error_handler


def ensure_documents_drive_url_column() -> None:
  with engine.begin() as connection:
    inspector = inspect(connection)
    if "documents" not in inspector.get_table_names():
      return

    columns = {column["name"] for column in inspector.get_columns("documents")}
    if "drive_url" not in columns:
      connection.execute(text("ALTER TABLE documents ADD COLUMN drive_url VARCHAR"))
      print("Added missing documents.drive_url column.")


ensure_documents_drive_url_column()
Base.metadata.create_all(bind=engine)


#Base.metadata.create_all(bind=engine)
print("Database and tables created successfully!")


class SecurityHeaders(BaseHTTPMiddleware):
  async def dispatch(self, request, call_next):
    docs_paths = {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}
    if request.url.path in docs_paths:
      return await call_next(request)

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


app=FastAPI(title="TutoratUp API")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Attach rate limiter to FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)

# Add SlowAPI middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SecurityHeaders)

# Log email service status on startup
log_email_status()

# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:19006",
    "http://127.0.0.1:19006",
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(autth1.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(parents.router)
app.include_router(users.router)
app.include_router(reports.router)
app.include_router(evaluation.router)
app.include_router(documents.router)
app.include_router(session.router)
app.include_router(quotes.router)
app.include_router(services.router)
app.include_router(notifications.router)
app.include_router(messages.router)
app.include_router(email_verification.router)
app.include_router(admin.router)
app.include_router(chatbot.router)
app.include_router(chatbot.api_router)

@app.get("/")
def read_root():
  return {"message": "Welcome to the TutoratUp API!"}








    




