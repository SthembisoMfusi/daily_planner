"""
Database models for the Daily Planner App.

Defines the SQLAlchemy ORM models for DayLog and MentorshipSession.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class DayLog(Base):
    """
    Represents a daily log entry.
    
    Attributes:
        id (int): Primary key.
        date (Date): The date of the log.
        notes (str): Optional notes for the day.
        sessions (list[MentorshipSession]): List of sessions for this day.
    """
    __tablename__ = 'day_logs'

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    sessions = relationship("MentorshipSession", back_populates="day_log", cascade="all, delete-orphan")

class MentorshipSession(Base):
    """
    Represents a single mentorship session.

    Attributes:
        id (int): Primary key.
        day_log_id (int): Foreign key to DayLog.
        group_name (str): Name or number of the group/mentee.
        category (str): Type of session (e.g., "1:1 Mentoring").
        activity_description (str): Description of what was done.
        duration_hours (int): Duration hours.
        duration_minutes (int): Duration minutes.
    """
    __tablename__ = 'mentorship_sessions'

    id = Column(Integer, primary_key=True)
    day_log_id = Column(Integer, ForeignKey('day_logs.id'), nullable=False)
    group_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    activity_description = Column(Text, nullable=True)
    duration_hours = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=0)

    day_log = relationship("DayLog", back_populates="sessions")

def get_engine():
    """Creates and returns the SQLAlchemy engine."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return create_engine(DATABASE_URL)

def init_db():
    """Initializes the database by creating all tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Generator that yields a database session.
    
    Yields:
        Session: SQLAlchemy session.
    """
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
