"""
CRUD operations for the Daily Planner App.

Functions to Create, Read, Update, and Delete DayLogs and MentorshipSessions.
"""
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import DayLog, MentorshipSession

def get_day_log(db: Session, log_date: date) -> Optional[DayLog]:
    """
    Retrieves a DayLog for a specific date.

    Args:
        db (Session): The database session.
        log_date (date): The date to retrieve the log for.

    Returns:
        Optional[DayLog]: The DayLog object if found, else None.
    """
    return db.query(DayLog).filter(DayLog.date == log_date).first()

def create_day_log(db: Session, log_date: date, notes: str = None) -> DayLog:
    """
    Creates a new DayLog entry for a specific date.

    Args:
        db (Session): The database session.
        log_date (date): The date for the new log.
        notes (str, optional): Initial notes for the day. Defaults to None.

    Returns:
        DayLog: The newly created DayLog object.
    """
    db_log = DayLog(date=log_date, notes=notes)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_day_log_notes(db: Session, log_date: date, notes: str) -> Optional[DayLog]:
    """
    Updates the notes for a specific DayLog.

    Args:
        db (Session): The database session.
        log_date (date): The date of the log to update.
        notes (str): The new notes content.

    Returns:
        Optional[DayLog]: The updated DayLog object if found, else None.
    """
    db_log = get_day_log(db, log_date)
    if db_log:
        db_log.notes = notes
        db.commit()
        db.refresh(db_log)
    return db_log

def add_mentorship_session(
    db: Session, 
    log_date: date, 
    group_name: str, 
    category: str, 
    activity: str, 
    hours: int, 
    minutes: int
) -> MentorshipSession:
    """
    Adds a new mentorship session to a day.
    
    If the DayLog for the specified date doesn't exist, it is automatically created.

    Args:
        db (Session): The database session.
        log_date (date): The date of the session.
        group_name (str): The name or number of the mentee/group.
        category (str): The category of the session (e.g., '1:1 Mentoring').
        activity (str): A description of the activity performed.
        hours (int): Duration of the session in hours.
        minutes (int): Duration of the session in minutes.

    Returns:
        MentorshipSession: The newly created session object.
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

def get_sessions_for_day(db: Session, log_date: date) -> List[MentorshipSession]:
    """
    Returns all mentorship sessions for a specific date.

    Args:
        db (Session): The database session.
        log_date (date): The date to retrieve sessions for.

    Returns:
        List[MentorshipSession]: A list of MentorshipSession objects. Returns an empty list if no sessions found.
    """
    db_log = get_day_log(db, log_date)
    if db_log:
        return db_log.sessions
    return []

def delete_session(db: Session, session_id: int) -> bool:
    """
    Deletes a mentorship session by its ID.

    Args:
        db (Session): The database session.
        session_id (int): The ID of the session to delete.

    Returns:
        bool: True if the session was found and deleted, False otherwise.
    """
    session = db.query(MentorshipSession).filter(MentorshipSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

def update_mentorship_session(
    db: Session,
    session_id: int,
    group_name: str,
    category: str,
    activity: str,
    hours: int,
    minutes: int
) -> Optional[MentorshipSession]:
    """
    Updates an existing mentorship session.

    Args:
        db (Session): The database session.
        session_id (int): The ID of the session to update.
        group_name (str): The new group name.
        category (str): The new category.
        activity (str): The new activity description.
        hours (int): The new duration hours.
        minutes (int): The new duration minutes.

    Returns:
        Optional[MentorshipSession]: The updated session object if found, else None.
    """
    session = db.query(MentorshipSession).filter(MentorshipSession.id == session_id).first()
    if session:
        session.group_name = group_name
        session.category = category
        session.activity_description = activity
        session.duration_hours = hours
        session.duration_minutes = minutes
        db.commit()
        db.refresh(session)
    return session
