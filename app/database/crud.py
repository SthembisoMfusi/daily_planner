"""
CRUD operations for the Daily Planner App.

Functions to Create, Read, Update, and Delete DayLogs and MentorshipSessions.
"""
from datetime import date
from sqlalchemy.orm import Session
from .models import DayLog, MentorshipSession

def get_day_log(db: Session, log_date: date):
    """Retrieves a DayLog for a specific date."""
    return db.query(DayLog).filter(DayLog.date == log_date).first()

def create_day_log(db: Session, log_date: date, notes: str = None):
    """Creates a new DayLog."""
    db_log = DayLog(date=log_date, notes=notes)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_day_log_notes(db: Session, log_date: date, notes: str):
    """Updates the notes for a specific DayLog."""
    db_log = get_day_log(db, log_date)
    if db_log:
        db_log.notes = notes
        db.commit()
        db.refresh(db_log)
    return db_log

def add_mentorship_session(db: Session, log_date: date, group_name: str, category: str, activity: str, hours: int, minutes: int):
    """
    Adds a new mentorship session to a day.
    
    If the DayLog doesn't exist, it is created.
    """
    db_log = get_day_log(db, log_date)
    if not db_log:
        db_log = create_day_log(db, log_date)
    
    session = MentorshipSession(
        day_log_id=db_log.id,
        group_name=group_name,
        category=category,
        activity_description=activity,
        duration_hours=hours,
        duration_minutes=minutes
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_sessions_for_day(db: Session, log_date: date):
    """Returns all sessions for a specific date."""
    db_log = get_day_log(db, log_date)
    if db_log:
        return db_log.sessions
    return []

def delete_session(db: Session, session_id: int):
    """Deletes a mentorship session by ID."""
    session = db.query(MentorshipSession).filter(MentorshipSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
