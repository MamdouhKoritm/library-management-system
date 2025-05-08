import unittest
from unittest.mock import patch, MagicMock
import sys

# Import LibraryApp from app.py
sys.path.append(".")
from app import LibraryApp, init_db

class TestLibraryApp(unittest.TestCase):
    @patch('mysql.connector.connect')
    def test_init_db_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        # Define side effects for fetchone() to match all calls in init_db()
        fetchone_side_effects = [
            None,  # SHOW TABLES LIKE 'BookRecord'
            None,  # SHOW COLUMNS FROM BookRecord LIKE 'Category'
            None,  # SHOW COLUMNS FROM BookRecord LIKE 'Price'
            ('BookName', 'varchar(50)', 'YES', '', None, ''),  # SHOW COLUMNS FROM BookRecord LIKE 'BookName'
            (0,),  # SELECT COUNT(*) FROM BookRecord
            None,  # SHOW TABLES LIKE 'UserRecord'
            None,  # SHOW TABLES LIKE 'AdminRecord'
            None,  # SHOW TABLES LIKE 'Feedback'
            None,  # SHOW COLUMNS FROM UserRecord LIKE 'BorrowDate' (first call)
            None,  # SHOW COLUMNS FROM UserRecord LIKE 'Fine' (first call)
        ]
        mock_cursor.fetchone.side_effect = fetchone_side_effects

        # Instantiate LibraryApp to trigger initialize_database
        app = LibraryApp()
        app.initialize_database()

        # Verify database setup calls
        mock_cursor.execute.assert_any_call("CREATE DATABASE IF NOT EXISTS Library")
        mock_cursor.execute.assert_any_call("USE Library")
        mock_cursor.execute.assert_any_call("CREATE TABLE BookRecord(BookID varchar(10) PRIMARY KEY, BookName varchar(50), Author varchar(30), Publisher varchar(30), Category varchar(20), Price DECIMAL(10,2))")
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