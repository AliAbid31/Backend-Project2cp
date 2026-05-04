from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum

class ReportType(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"

class ReportCreate(BaseModel):
    reason: str
    description: str
    report_type: ReportType
    screenshot_path: Optional[str] = None

class TeacherReportCreate(ReportCreate):
    teacher_id: int
    report_type: ReportType = ReportType.TEACHER

class StudentReportCreate(ReportCreate):
    evaluation_id: int
    report_type: ReportType = ReportType.STUDENT

# Specific Scenario Schemas
class StudentReportStudentRequest(BaseModel):
    """Student reporting another student via evaluation comment"""
    evaluation_id: int
    reason: str
    description: str
    screenshot_path: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class StudentReportTeacherRequest(BaseModel):
    """Student reporting a teacher they had a session with"""
    teacher_id: int
    reason: str
    description: str
    screenshot_path: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class TeacherReportStudentRequest(BaseModel):
    """Teacher reporting a student via evaluation comment"""
    evaluation_id: int
    reason: str
    description: str
    screenshot_path: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class Report(BaseModel):
    id: int
    reason: str
    description: str
    report_type: str
    reporter_id: int
    teacher_id: Optional[int] = None
    student_id: Optional[int] = None
    evaluation_id: Optional[int] = None
    screenshot_path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
