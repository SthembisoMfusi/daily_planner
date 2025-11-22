import random
from datetime import date, timedelta, datetime
from app.database import init_db, get_db
from app.database.models import DayLog, MentorshipSession

def populate_calendar():
    print("Initializing database...")
    init_db()
    
    # Date range: 2025-10-20 to 2025-11-20
    start_date = date(2025, 10, 20)
    end_date = date(2025, 11, 20)
    
    # Activities and descriptions
    activities = [
        ("Code Review", "Reviewed current assignment progress."),
        ("Code Review", "Went through code quality checks and linting errors."),
        ("Pair Programming", "Worked together on a code question with one person typing and another person giving directions."),
        ("Pair Programming", "Paired up the mentees to help each other with the assignment they had to do for the week."),
        ("1:1", "Weekly sync to check in on blockers and challenges."),
        ("1:1", "Performance review and feedback session.")
    ]
    
    # Use static group name
    group_name = "Group 26"
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Clear existing data for the date range
        print("Clearing existing data for date range...")
        existing_day_logs = db.query(DayLog).filter(
            DayLog.date >= start_date,
            DayLog.date <= end_date
        ).all()
        for day_log in existing_day_logs:
            db.delete(day_log)
        db.commit()
        print(f"Cleared {len(existing_day_logs)} existing day logs.")
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            print(f"Processing {current_date}...")
            
            # Check if DayLog exists
            day_log = db.query(DayLog).filter(DayLog.date == current_date).first()
            if not day_log:
                day_log = DayLog(date=current_date)
                db.add(day_log)
                db.commit()
                db.refresh(day_log)
            
            # Special event on Nov 17
            if current_date == date(2025, 11, 17):
                session = MentorshipSession(
                    day_log_id=day_log.id,
                    group_name=group_name,
                    category="Assessment",
                    activity_description="Mentees wrote a test covering recent topics.",
                    duration_hours=2,
                    duration_minutes=0
                )
                db.add(session)
            else:
                # Generate random sessions to sum up to ~2 hours
                # We'll do 1 or 2 sessions per day
                num_sessions = random.randint(1, 2)
                total_minutes = 0
                target_minutes = 120 # 2 hours
                
                for i in range(num_sessions):
                    category, description = random.choice(activities)
                    
                    # Split time roughly
                    if num_sessions == 1:
                        minutes = target_minutes + random.randint(-15, 15)
                    else:
                        if i == 0:
                            minutes = random.randint(45, 75)
                        else:
                            minutes = target_minutes - total_minutes + random.randint(-10, 10)
                    
                    # Ensure positive minutes
                    minutes = max(30, minutes)
                    total_minutes += minutes
                    
                    hours = minutes // 60
                    mins = minutes % 60
                    
                    session = MentorshipSession(
                        day_log_id=day_log.id,
                        group_name=group_name,
                        category=category,
                        activity_description=description,
                        duration_hours=hours,
                        duration_minutes=mins
                    )
                    db.add(session)
            
            db.commit()
            current_date += timedelta(days=1)
            
        print("Calendar population complete!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_calendar()
