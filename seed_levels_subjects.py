import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.teaching_level import TeachingLevel
from app.models.subject import Subject
from app.models.association_level_subject import level_subjects
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def get_or_create_subject(name):
    name = name.strip()
    subject = db.query(Subject).filter(Subject.name == name).first()
    if not subject:
        subject = Subject(name=name)
        db.add(subject)
        db.flush()
    return subject

def get_or_create_level(name):
    name = name.strip()
    level = db.query(TeachingLevel).filter(TeachingLevel.name == name).first()
    if not level:
        level = TeachingLevel(name=name)
        db.add(level)
        db.flush()
    return level

# Data from PDF (formatted to match frontend/database)
data = {
    "Primary School - 1st Year": ["Arabic language", "Mathematics", "Islamic education"],
    "Primary School - 2nd Year": ["Arabic language", "Mathematics", "Islamic education"],
    "Primary School - 3rd Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Scientific and Technological Education", "History"],
    "Primary School - 4th Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Scientific and Technological Education", "History"],
    "Primary School - 5th Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Scientific and Technological Education", "History & Geography", "Civil education"],
    
    "Middle School - 1st Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Physics", "Natural and life Science", "History & Geography", "Civil education"],
    "Middle School - 2nd Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Physics", "Natural and life Science", "History & Geography", "Civil education"],
    "Middle School - 3rd Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Physics", "Natural and life Science", "History & Geography", "Civil education"],
    "Middle School - 4th Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Physics", "Natural and life Science", "History & Geography", "Civil education"],
    
    # High School with streams (keeping generic names too for matching)
    "High School - 1st Year": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Physics", "Natural and life Science", "History & Geography"],
    "High School - 1st Year (Scientific)": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "Physics", "Natural and life Science", "History & Geography"],
    "High School - 1st Year (Literature)": ["Arabic language", "Mathematics", "Islamic education", "French language", "English language", "History & Geography"],
    
    "High School - 2nd Year": ["Natural and life Science", "Physics", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Mechanical engineering", "Electrical engineering", "Process engineering", "Civil engineering", "Philosophy", "Economics", "Management", "German language", "Russian language", "Italian language", "Spanish language"],
    "High School - 2nd Year (Science Stream)": ["Natural and life Science", "Physics", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language"],
    "High School - 2nd Year (Technical Stream)": ["Mechanical engineering", "Electrical engineering", "Process engineering", "Civil engineering", "Physics", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language"],
    "High School - 2nd Year (Mathematics Stream)": ["Mathematics", "Physics", "Natural and life Science", "Arabic language", "History & Geography", "Islamic education", "French language", "English language"],
    "High School - 2nd Year (Letters & Philosophy)": ["Philosophy", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Mathematics"],
    "High School - 2nd Year (Management & Economics)": ["Economics", "Management", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language"],
    "High School - 2nd Year (Foreign Languages)": ["German language", "Russian language", "Italian language", "Spanish language", "French language", "English language", "Arabic language", "History & Geography", "Islamic education", "Mathematics"],
    
    "High School - 3rd Year": ["Natural and life Science", "Physics", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Philosophy", "Mechanical engineering", "Electrical engineering", "Process engineering", "Civil engineering", "Economics", "Management", "German language", "Russian language", "Italian language", "Spanish language"],
    "High School - 3rd Year (Science Stream)": ["Natural and life Science", "Physics", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Philosophy"],
    "High School - 3rd Year (Technical Stream)": ["Mechanical engineering", "Electrical engineering", "Process engineering", "Civil engineering", "Physics", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Philosophy"],
    "High School - 3rd Year (Mathematics Stream)": ["Mathematics", "Physics", "Natural and life Science", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Philosophy"],
    "High School - 3rd Year (Letters & Philosophy)": ["Philosophy", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Mathematics"],
    "High School - 3rd Year (Management & Economics)": ["Economics", "Management", "Mathematics", "Arabic language", "History & Geography", "Islamic education", "French language", "English language", "Philosophy"],
    "High School - 3rd Year (Foreign Languages)": ["German language", "Russian language", "Italian language", "Spanish language", "French language", "English language", "Arabic language", "Philosophy", "History & Geography", "Islamic education", "Mathematics"],
    
    "University - 1st Year": ["ALG1", "ANA1", "ALSDS", "ARCHI1", "SYS1", "ELECT", "BWEB", "TEE", "ANA2", "ALG2", "SYS2", "ALSDD", "ELECF1", "MECA", "TEO", "ANG1"],
    "University - 2nd Year": ["ALG3", "ANA3", "SFSD", "ARCHI2", "PRST1", "ELECF2", "ECON", "ANG2", "ANA4", "PRST2", "POO", "OOE", "SINF", "LOGM", "PRJT", "ANG3"],
    "University - 3rd Year": ["ANUM", "IGL", "ORGA", "RES1", "RO", "SYC", "THP", "English", "ARCHI3", "BDD", "CPRJ", "MCSI", "PRJT", "RES2", "SEC", "SYC2"],
    
    "University - 4th Year": ["ANAD", "BDA", "CRP", "HPC", "INFOVIS", "MASD", "ML", "SGOV", "SIGA", "TSG", "BI", "IMN", "IRIAD", "NLP", "PMSS", "RCR", "RV", "TOAI", "COMPIL", "FAS", "RESA", "STAGE", "TPGO", "VCL", "ALOG", "OPTM", "PRJT", "SSR", "SYSR", "IHM", "MAGIL", "OUTILS", "PDC", "WEB", "BDM", "ENTP", "MBL1", "MBL2", "MNG", "QLOG", "AQUA", "ASI", "MPSI", "SIAD", "TICO", "AL", "AUDIT", "COFI", "CRM", "ERP", "FASI", "MSSI", "PRJT_SSI", "SIC", "URBA"],
    "University - 4th Year (SID)": ["ANAD", "BDA", "CRP", "HPC", "INFOVIS", "MASD", "ML", "SGOV", "SIGA", "TSG", "BI", "IMN", "IRIAD", "NLP", "PMSS", "RCR", "RV", "TOAI"],
    "University - 4th Year (SIQ)": ["ANAD", "COMPIL", "FAS", "RESA", "STAGE", "TPGO", "VCL", "ALOG", "BDA", "OPTM", "PRJT", "SSR", "SYSR"],
    "University - 4th Year (SIL)": ["ANAD", "COMPIL", "IHM", "MAGIL", "OUTILS", "PDC", "STAGE", "TPGO", "VCL", "WEB", "ALOG", "BDA", "BDM", "ENTP", "IHM", "MBL1", "MBL2", "MNG", "QLOG"],
    "University - 4th Year (SIT)": ["ANAD", "AQUA", "ASI", "BDA", "IHM", "MPSI", "SIAD", "SIGA", "TICO", "AL", "AUDIT", "COFI", "CRM", "ERP", "FASI", "MSSI", "PRJT", "PRJT_SSI", "SIC", "URBA"],
    
    "University - 5th Year+": ["Final Year Project / Internship", "General help in any subject"]
}

try:
    for level_name, subject_names in data.items():
        level = get_or_create_level(level_name)
        for sub_name in subject_names:
            subject = get_or_create_subject(sub_name)
            if subject not in level.subjects:
                level.subjects.append(subject)
    db.commit()
    print("Seeding complete.")
except Exception as e:
    db.rollback()
    print(f"Error during seeding: {e}")
finally:
    db.close()
