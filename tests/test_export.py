import unittest
import os
import shutil
from datetime import date
from unittest.mock import MagicMock, patch
from app.export import export_to_excel

class TestExport(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_exports"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # Clean up export file if it exists
        export_file = os.path.join("exports", "test_export.xlsx")
        if os.path.exists(export_file):
            os.remove(export_file)

    @patch('app.export.get_engine')
    @patch('app.export.sessionmaker')
    def test_export_to_excel(self, mock_sessionmaker, mock_get_engine):
        # Mock DB session
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        
        # Mock query results
        class MockRow:
            def __init__(self, d, g, c, a, h, m):
                self.date = d
                self.group_name = g
                self.category = c
                self.activity_description = a
                self.duration_hours = h
                self.duration_minutes = m

        mock_data = [
            MockRow(date(2023, 1, 1), "G1", "Cat1", "Act1", 1, 0),
            MockRow(date(2023, 1, 8), "G2", "Cat2", "Act2", 2, 0)
        ]
        
        mock_session.query.return_value.join.return_value.order_by.return_value.all.return_value = mock_data
        
        # Run export
        filename = "test_export.xlsx"
        success, msg = export_to_excel(filename=filename)
        
        self.assertTrue(success, msg)
        expected_path = os.path.join("exports", filename)
        self.assertTrue(os.path.exists(expected_path))
        
        import pandas as pd
        xl = pd.ExcelFile(expected_path)
        self.assertEqual(len(xl.sheet_names), 2)

if __name__ == '__main__':
    unittest.main()
