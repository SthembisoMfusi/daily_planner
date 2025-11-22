from app.database import get_db
from app.database.models import DayLog, MentorshipSession

def verify_group_names():
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Get all sessions
        sessions = db.query(MentorshipSession).all()
        
        # Check if all use "Group 26"
        group_names = set(s.group_name for s in sessions)
        
        print(f"Total sessions: {len(sessions)}")
        print(f"Unique group names: {group_names}")
        
        if group_names == {"Group 26"}:
            print("✓ All sessions use 'Group 26'")
        else:
            print("✗ Some sessions use different group names!")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_group_names()
