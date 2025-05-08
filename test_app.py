import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Import LibraryApp from app.py
sys.path.append(".")
from app import LibraryApp, init_db

class TestLibraryApp(unittest.TestCase):
    def setUp(self):
        # Set TEST_MODE to use SQLite
        os.environ["TEST_MODE"] = "1"

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('sqlite3.connect')
    def test_init_db_success(self, mock_connect, mock_print, mock_exit):
        # Mock the database connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        # Define side effects for fetchone() to match all calls in init_db() with SQLite
        fetchone_side_effects = [
            None,  # SELECT name FROM sqlite_master WHERE type='table' AND name='BookRecord'
            [('BookID', 'TEXT', 0, None, 1, None), ('BookName', 'TEXT', 1, None, 0, None), ('Author', 'TEXT', 2, None, 0, None), ('Publisher', 'TEXT', 3, None, 0, None), ('Category', 'TEXT', 4, None, 0, None), ('Price', 'REAL', 5, None, 0, None)],  # PRAGMA table_info(BookRecord)
            None,  # PRAGMA table_info(BookRecord) for Category (after adding)
            None,  # PRAGMA table_info(BookRecord) for Price (after adding)
            (0,),  # SELECT COUNT(*) FROM BookRecord
            None,  # SELECT name FROM sqlite_master WHERE type='table' AND name='UserRecord'
            None,  # PRAGMA table_info(UserRecord) for BorrowDate (after adding)
            None,  # PRAGMA table_info(UserRecord) for Fine (after adding)
            None,  # SELECT name FROM sqlite_master WHERE type='table' AND name='AdminRecord'
            None,  # SELECT name FROM sqlite_master WHERE type='table' AND name='Feedback'
        ]
        mock_cursor.fetchone.side_effect = fetchone_side_effects

        # Mock commit to avoid issues
        mock_db.commit = MagicMock()

        # Instantiate LibraryApp to trigger initialize_database
        app = LibraryApp()
        app.initialize_database()

        # Verify sys.exit() was not called
        mock_exit.assert_not_called()

        # Verify database setup calls with SQLite syntax
        mock_cursor.execute.assert_any_call("CREATE DATABASE IF NOT EXISTS Library")
        mock_cursor.execute.assert_any_call("USE Library")
        mock_cursor.execute.assert_any_call("CREATE TABLE BookRecord(BookID TEXT PRIMARY KEY, BookName TEXT, Author TEXT, Publisher TEXT, Category TEXT, Price REAL)")
        mock_cursor.execute.assert_any_call("PRAGMA table_info(BookRecord)")
        mock_cursor.execute.assert_any_call("ALTER TABLE BookRecord ADD COLUMN Category TEXT")
        mock_cursor.execute.assert_any_call("ALTER TABLE BookRecord ADD COLUMN Price REAL")
        self.assertIsNotNone(app.mydb)
        self.assertIsNotNone(app.mycursor)

    @patch('mysql.connector.connect')
    def test_init_db_connection_failure(self, mock_connect):
        # Simulate a connection failure
        mock_connect.side_effect = Exception("Connection failed")

        # Instantiate LibraryApp and expect SystemExit during initialization
        with self.assertRaises(SystemExit):
            app = LibraryApp()
            app.initialize_database()

if __name__ == '__main__':
    unittest.main()