import unittest
from unittest.mock import patch, MagicMock
import sys

# Import init_db from app.py
sys.path.append(".")
from app import init_db

class TestLibraryApp(unittest.TestCase):
    @patch('mysql.connector.connect')
    def test_init_db_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        # Mock cursor responses
        mock_cursor.fetchone.side_effect = [
            None,  # SHOW TABLES LIKE 'BookRecord' -> Table doesn't exist
            None,  # SHOW COLUMNS FROM BookRecord LIKE 'Category' -> Column doesn't exist
            None,  # SHOW COLUMNS FROM BookRecord LIKE 'Price' -> Column doesn't exist
            ('varchar(50)',),  # SHOW COLUMNS FROM BookRecord LIKE 'BookName' -> Correct length
            (0,),  # SELECT COUNT(*) FROM BookRecord -> Table is empty
            None,  # SHOW TABLES LIKE 'UserRecord' -> Table doesn't exist
            None,  # SHOW TABLES LIKE 'AdminRecord' -> Table doesn't exist
            None   # SHOW TABLES LIKE 'Feedback' -> Table doesn't exist
        ]

        # Call init_db
        mydb, mycursor = init_db()

        # Verify database setup calls
        mock_cursor.execute.assert_any_call("CREATE DATABASE IF NOT EXISTS Library")
        mock_cursor.execute.assert_any_call("USE Library")
        mock_cursor.execute.assert_any_call("CREATE TABLE BookRecord(BookID varchar(10) PRIMARY KEY, BookName varchar(50), Author varchar(30), Publisher varchar(30), Category varchar(20), Price DECIMAL(10,2))")
        self.assertEqual(mydb, mock_db)
        self.assertEqual(mycursor, mock_cursor)

    @patch('mysql.connector.connect')
    def test_init_db_connection_failure(self, mock_connect):
        # Simulate a connection failure
        mock_connect.side_effect = Exception("Connection failed")

        # Call init_db and expect SystemExit
        with self.assertRaises(SystemExit):
            init_db()

if __name__ == '__main__':
    unittest.main()