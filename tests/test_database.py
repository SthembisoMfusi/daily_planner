import unittest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, DayLog, MentorshipSession
from app.database.crud import (
    create_day_log,
    add_mentorship_session,
    get_sessions_for_day,
    delete_session,
    get_day_log
)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_create_day_log(self):
        d = date(2023, 1, 1)
        log = create_day_log(self.db, d, "Test Notes")
        self.assertIsNotNone(log.id)
        self.assertEqual(log.date, d)
        self.assertEqual(log.notes, "Test Notes")

    def test_add_mentorship_session(self):
        d = date(2023, 1, 2)
        session = add_mentorship_session(
            self.db, d, "Group A", "Code Review", "Reviewing PRs", 1, 30
        )
        self.assertIsNotNone(session.id)
        self.assertEqual(session.group_name, "Group A")
        self.assertEqual(session.duration_hours, 1)
        self.assertEqual(session.duration_minutes, 30)
        
        # Verify DayLog was created implicitly
        log = get_day_log(self.db, d)
        self.assertIsNotNone(log)
        self.assertEqual(len(log.sessions), 1)

    def test_get_sessions_for_day(self):
        d = date(2023, 1, 3)
        add_mentorship_session(self.db, d, "G1", "Cat1", "Act1", 1, 0)
        add_mentorship_session(self.db, d, "G2", "Cat2", "Act2", 2, 0)
        
        sessions = get_sessions_for_day(self.db, d)
        self.assertEqual(len(sessions), 2)

    def test_delete_session(self):
        d = date(2023, 1, 4)
        session = add_mentorship_session(self.db, d, "G1", "Cat1", "Act1", 1, 0)
        session_id = session.id
        
        delete_session(self.db, session_id)
        
        sessions = get_sessions_for_day(self.db, d)
        self.assertEqual(len(sessions), 0)

if __name__ == '__main__':
    unittest.main()
