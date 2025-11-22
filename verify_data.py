from app.database import get_db
from app.database.models import DayLog, MentorshipSession
from sqlalchemy import func

def verify_data():
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Count DayLogs
        day_count = db.query(DayLog).count()
        print(f"Total DayLogs: {day_count}")
        
        # Count Sessions
        session_count = db.query(MentorshipSession).count()
        print(f"Total Sessions: {session_count}")
        
        # Check Nov 17
        nov_17_sessions = db.query(MentorshipSession).join(DayLog).filter(DayLog.date == '2025-11-17').all()
        print(f"Sessions on Nov 17: {len(nov_17_sessions)}")
        for s in nov_17_sessions:
            print(f" - {s.category}: {s.activity_description} ({s.duration_hours}h {s.duration_minutes}m)")
            
        # Check average duration
        total_duration_minutes = 0
        sessions = db.query(MentorshipSession).all()
        for s in sessions:
            total_duration_minutes += s.duration_hours * 60 + s.duration_minutes
            
        if day_count > 0:
            avg_daily_minutes = total_duration_minutes / day_count
            print(f"Average daily duration: {avg_daily_minutes:.2f} minutes")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()
