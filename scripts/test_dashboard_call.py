from app.database.database import SessionLocal
from app.crud import crud_admin
import traceback

def run():
    db = SessionLocal()
    try:
        stats = crud_admin.get_dashboard_stats(db)
        print('STATS OK', stats)
        top = crud_admin.get_top_performing_teachers(db, limit=3)
        print('TOP', top)
    except Exception as e:
        print('EXC', e)
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    run()
