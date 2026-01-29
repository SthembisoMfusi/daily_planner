import random
from datetime import date, timedelta, datetime
from typing import List, Set
from app.database import init_db, get_db
from app.database.models import DayLog, MentorshipSession

def get_date_input(prompt: str) -> date:
    while True:
        try:
            date_str = input(prompt + " (YYYY-MM-DD): ")
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD.")

def get_excluded_weekdays() -> Set[int]:
    print("\nWeekdays: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun")
    input_str = input("Enter weekdays to exclude (comma separated, e.g., '5,6' for weekends) [default: 5,6]: ")
    if not input_str.strip():
        return {5, 6}
    
    try:
        return {int(d.strip()) for d in input_str.split(",") if d.strip().isdigit()}
    except ValueError:
        print("Invalid input. Using default (Sat, Sun).")
        return {5, 6}

def populate_calendar():
    print("=== Daily Planner Population Tool ===\n")
    print("Initializing database...")
    init_db()
    
    start_date = get_date_input("\nEnter start date")
    end_date = get_date_input("Enter end date")
    
    if start_date > end_date:
        print("Error: Start date must be before end date.")
        return

    excluded_weekdays = get_excluded_weekdays()
    
    while True:
        try:
            target_hours = float(input("\nEnter target hours per day (e.g., 2.5): "))
            break
        except ValueError:
            print("Invalid number.")

    group_name = input("\nEnter Group Name [default: Group 26]: ") or "Group 26"

    # Activities and descriptions
    activities = [
        ("Code Review", "Reviewed current assignment progress."),
        ("Code Review", "Went through code quality checks and linting errors."),
        ("Pair Programming", "Worked together on a code question with one person typing and another person giving directions."),
        ("Pair Programming", "Paired up the mentees to help each other with the assignment they had to do for the week."),
        ("1:1", "Weekly sync to check in on blockers and challenges."),
        ("1:1", "Performance review and feedback session."),
        ("Debugging", "Helped mentees debug issues in their code."),
        ("Concept Explanation", "Explained core concepts related to the current module.")
    ]
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Clear existing data for the date range
        print("\nClearing existing data for date range...")
        existing_day_logs = db.query(DayLog).filter(
            DayLog.date >= start_date,
            DayLog.date <= end_date
        ).all()
        
        count = len(existing_day_logs)
        for day_log in existing_day_logs:
            db.delete(day_log)
        db.commit()
        print(f"Cleared {count} existing day logs.")
        
        current_date = start_date
        total_days_populated = 0
        
        while current_date <= end_date:
            # Skip excluded weekdays
            if current_date.weekday() in excluded_weekdays:
                current_date += timedelta(days=1)
                continue
            
            print(f"Processing {current_date}...")
            
            # Create/Get DayLog
            day_log = DayLog(date=current_date)
            db.add(day_log)
            db.commit()
            db.refresh(day_log)
            
            # Generate sessions
            num_sessions = random.randint(1, 3)
            target_minutes = int(target_hours * 60)
            current_minutes = 0
            
            for i in range(num_sessions):
                category, description = random.choice(activities)
                
                # Distribution logic
                remaining_minutes = target_minutes - current_minutes
                
                if i == num_sessions - 1:
                    # Last session takes remaining time
                    minutes = remaining_minutes
                else:
                    # Random chunk of remaining time
                    max_chunk = remaining_minutes - (30 * (num_sessions - 1 - i)) # Leave at least 30m for others
                    if max_chunk < 30: 
                        max_chunk = 30
                    minutes = random.randint(30, max_chunk)
                
                # Jitter (+/- 10 mins) but enforce min 15
                minutes += random.randint(-10, 10)
                minutes = max(15, minutes)
                
                current_minutes += minutes
                
                hours_part = minutes // 60
                mins_part = minutes % 60
                
                session = MentorshipSession(
                    day_log_id=day_log.id,
                    group_name=group_name,
                    category=category,
                    activity_description=description,
                    duration_hours=hours_part,
                    duration_minutes=mins_part
                )
                db.add(session)
            
            db.commit()
            total_days_populated += 1
            current_date += timedelta(days=1)
            
        print(f"\nSuccess! Populated {total_days_populated} days.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_calendar()
