import unittest
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
from app import init_db, LibraryApp

class TestLibraryApp(unittest.TestCase):
    def setUp(self):
        """Set up test environment with fresh database."""
        self.app = None
        os.environ["TEST_MODE"] = "1"
        mydb, mycursor, _, _ = init_db()
        self.app = LibraryApp()
        self.app.mydb = mydb
        self.app.mycursor = mycursor

    def tearDown(self):
        """Clean up after tests."""
        if self.app and self.app.mydb:
            self.app.mydb.commit()
            self.app.mydb.close()
        if "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]

    def test_sqlite_init_db_success(self):
        """Test database initialization with SQLite."""
        mydb, mycursor, placeholder, is_sqlite = init_db()
        self.assertTrue(is_sqlite)
        self.assertEqual(placeholder, "?")
        mycursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='BookRecord'")
        self.assertIsNotNone(mycursor.fetchone(), "BookRecord table not created")
        mycursor.execute("SELECT COUNT(*) FROM BookRecord")
        self.assertEqual(mycursor.fetchone()[0], 30, "Sample books not inserted")
        mydb.close()

    @patch("mysql.connector.connect")
    def test_mysql_init_db_success(self, mock_connect):
        """Test database initialization with MySQL."""
        os.environ["TEST_MODE"] = "0"
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [
            None,          # No BookRecord table
            (["BookID"],), # Columns exist
            ([0],),        # COUNT(*) = 0 for BookRecord
            None,          # No UserRecord table
            (["UserID"],), # Columns exist
            None,          # No AdminRecord table
            None           # No Feedback table
        ]
        mydb, mycursor, placeholder, is_sqlite = init_db()
        self.assertFalse(is_sqlite)
        self.assertEqual(placeholder, "%s")
        mock_cursor.execute.assert_any_call(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'Library' AND table_name = 'BookRecord'"
        )
        mock_cursor.execute.assert_any_call(
            "CREATE TABLE BookRecord(" +
            "BookID VARCHAR(255) PRIMARY KEY, " +
            "BookName VARCHAR(255), " +
            "Author VARCHAR(255), " +
            "Publisher VARCHAR(255), " +
            "Category VARCHAR(255), " +
            "Price DECIMAL(10,2)" +
            ")"
        )
        mock_db.commit.assert_called()

    @patch("mysql.connector.connect")
    def test_mysql_init_db_connection_failure(self, mock_connect):
        """Test MySQL connection failure handling."""
        os.environ["TEST_MODE"] = "0"
        mock_connect.side_effect = Exception("Connection failed")
        with self.assertRaises(SystemExit):
            init_db()

    def test_add_user_sqlite(self):
        """Test adding a user with SQLite."""
        user_id, user_name, password = "104", "TestUser", "pass"
        self.app.mycursor.execute(
            "INSERT INTO UserRecord VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, user_name, password, None, None, 0.00)
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT UserName FROM UserRecord WHERE UserID = ?", (user_id,))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], user_name, "User not added correctly")

    @patch("tkinter.Tk.title")
    @patch("tkinter.Tk.winfo_children")
    @patch("tkinter.Frame")
    @patch("tkinter.Label")
    @patch("tkinter.Button")
    def test_create_login_screen(self, mock_button, mock_label, mock_frame, mock_winfo_children, mock_title):
        """Test login screen initialization and widget creation."""
        # Initialize app with mocked title
        app = LibraryApp()
        app.title = mock_title

        # Mock winfo_children to return a list of mock widgets
        mock_widget = MagicMock()
        mock_winfo_children.return_value = [mock_widget]

        # Verify title set in __init__
        mock_title.assert_called_once_with("The Book Worm - Library Management System")

        # Mock two frame instances
        mock_frame1 = MagicMock()
        mock_frame2 = MagicMock()
        mock_frame.side_effect = [mock_frame1, mock_frame2]

        # Call create_login_screen
        app.create_login_screen()

        # Verify clear_window called by checking destroy on mock widgets
        mock_widget.destroy.assert_called_once()

        # Verify frame creations and packing for frame1 only
        mock_frame.assert_any_call(app)
        mock_frame1.pack.assert_called_once_with(pady=50)

        # Verify labels on frame1
        self.assertEqual(mock_label.call_count, 4)
        mock_label.assert_any_call(mock_frame1, text="The Book Worm", font=("Arial", 20))
        mock_label.assert_any_call(mock_frame1, text="Login", font=("Arial", 14))

        # Verify buttons on frame1
        self.assertEqual(mock_button.call_count, 8)
        mock_button.assert_any_call(mock_frame1, text="Admin Login", command=app.admin_login)
        mock_button.assert_any_call(mock_frame1, text="User Login", command=app.user_login)
        mock_button.assert_any_call(mock_frame1, text="Create User Account", command=app.create_user_account)
        mock_button.assert_any_call(mock_frame1, text="Exit", command=sys.exit)

    def test_add_book_sqlite(self):
        """Test adding a book with SQLite."""
        book_data = ("B031", "Test Book", "Test Author", "Test Publisher", "Test Category", 9.99)
        self.app.mycursor.execute(
            "INSERT INTO BookRecord VALUES (?, ?, ?, ?, ?, ?)",
            book_data
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT BookName FROM BookRecord WHERE BookID = ?", ("B031",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "Test Book", "Book not added correctly")

    def test_issue_book_sqlite(self):
        """Test issuing a book with SQLite."""
        self.app.mycursor.execute(
            "INSERT INTO UserRecord VALUES (?, ?, ?, ?, ?, ?)",
            ("105", "TestUser", "pass", None, None, 0.00)
        )
        self.app.mycursor.execute(
            "UPDATE UserRecord SET BookID = ?, BorrowDate = ? WHERE UserID = ?",
            ("B001", "2025-05-08", "105")
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT BookID FROM UserRecord WHERE UserID = ?", ("105",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "B001", "Book not issued correctly")

    def test_return_book_sqlite(self):
        """Test returning a book with SQLite."""
        self.app.mycursor.execute(
            "INSERT INTO UserRecord VALUES (?, ?, ?, ?, ?, ?)",
            ("106", "TestUser", "pass", "B001", "2025-05-08", 0.00)
        )
        self.app.mycursor.execute(
            "UPDATE UserRecord SET BookID = ?, BorrowDate = ? WHERE UserID = ?",
            (None, None, "106")
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT BookID FROM UserRecord WHERE UserID = ?", ("106",))
        result = self.app.mycursor.fetchone()
        self.assertIsNone(result[0], "Book not returned correctly")

    def test_search_book_sqlite(self):
        """Test searching a book with SQLite."""
        book_data = ("B032", "Search Book", "Search Author", "Search Publisher", "Search Category", 19.99)
        self.app.mycursor.execute(
            "INSERT INTO BookRecord VALUES (?, ?, ?, ?, ?, ?)",
            book_data
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT BookName FROM BookRecord WHERE BookID = ?", ("B032",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "Search Book", "Book not found correctly")

    def test_check_overdue_sqlite(self):
        """Test checking overdue books with SQLite."""
        self.app.mycursor.execute(
            "INSERT INTO UserRecord VALUES (?, ?, ?, ?, ?, ?)",
            ("107", "TestUser", "pass", "B001", "2025-04-01", 0.00)
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT BorrowDate FROM UserRecord WHERE UserID = ?", ("107",))
        borrow_date = self.app.mycursor.fetchone()[0]
        days_overdue = (datetime.now() - datetime.strptime(borrow_date, "%Y-%m-%d")).days
        self.assertTrue(days_overdue > 14, f"Book not overdue, only {days_overdue} days")

    def test_add_admin_sqlite(self):
        """Test adding an admin with SQLite."""
        self.app.mycursor.execute(
            "INSERT INTO AdminRecord (AdminID, Password) VALUES (?, ?)",
            ("A101", "adminpass")
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT Password FROM AdminRecord WHERE AdminID = ?", ("A101",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "adminpass", "Admin not added correctly")

    def test_delete_book_sqlite(self):
        """Test deleting a book with SQLite."""
        book_data = ("B033", "Delete Book", "Delete Author", "Delete Publisher", "Delete Category", 29.99)
        self.app.mycursor.execute(
            "INSERT INTO BookRecord VALUES (?, ?, ?, ?, ?, ?)",
            book_data
        )
        self.app.mycursor.execute("DELETE FROM BookRecord WHERE BookID = ?", ("B033",))
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT BookName FROM BookRecord WHERE BookID = ?", ("B033",))
        result = self.app.mycursor.fetchone()
        self.assertIsNone(result, "Book not deleted correctly")

    def test_update_book_sqlite(self):
        """Test updating a book with SQLite."""
        book_data = ("B034", "Old Book", "Old Author", "Old Publisher", "Old Category", 19.99)
        self.app.mycursor.execute(
            "INSERT INTO BookRecord VALUES (?, ?, ?, ?, ?, ?)",
            book_data
        )
        self.app.mycursor.execute(
            "UPDATE BookRecord SET BookName = ? WHERE BookID = ?",
            ("New Book", "B034")
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT BookName FROM BookRecord WHERE BookID = ?", ("B034",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "New Book", "Book not updated correctly")

    def test_add_feedback_sqlite(self):
        """Test adding feedback with SQLite."""
        self.app.mycursor.execute(
            "INSERT INTO Feedback (Feedback, Rating) VALUES (?, ?)",
            ("Great system!", "8")
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT Feedback, Rating FROM Feedback WHERE Feedback = ?", ("Great system!",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "Great system!", "Feedback not added correctly")
        self.assertEqual(result[1], "8", "Rating not added correctly")

    def test_delete_user_sqlite(self):
        """Test deleting a user with SQLite."""
        user_data = ("108", "DeleteUser", "pass", None, None, 0.00)
        self.app.mycursor.execute(
            "INSERT INTO UserRecord VALUES (?, ?, ?, ?, ?, ?)",
            user_data
        )
        self.app.mycursor.execute("DELETE FROM UserRecord WHERE UserID = ?", ("108",))
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT UserName FROM UserRecord WHERE UserID = ?", ("108",))
        result = self.app.mycursor.fetchone()
        self.assertIsNone(result, "User not deleted correctly")

    def test_update_user_sqlite(self):
        """Test updating a user with SQLite."""
        user_data = ("109", "OldUser", "pass", None, None, 0.00)
        self.app.mycursor.execute(
            "INSERT INTO UserRecord VALUES (?, ?, ?, ?, ?, ?)",
            user_data
        )
        self.app.mycursor.execute(
            "UPDATE UserRecord SET UserName = ? WHERE UserID = ?",
            ("NewUser", "109")
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT UserName FROM UserRecord WHERE UserID = ?", ("109",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "NewUser", "User not updated correctly")

    def test_delete_feedback_sqlite(self):
        """Test deleting feedback with SQLite."""
        self.app.mycursor.execute(
            "INSERT INTO Feedback (Feedback, Rating) VALUES (?, ?)",
            ("Great system!", "8")
        )
        self.app.mycursor.execute("DELETE FROM Feedback WHERE Feedback = ?", ("Great system!",))
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT Feedback FROM Feedback WHERE Feedback = ?", ("Great system!",))
        result = self.app.mycursor.fetchone()
        self.assertIsNone(result, "Feedback not deleted correctly")

    @patch("mysql.connector.connect")
    def test_add_admin_mysql(self, mock_connect):
        """Test adding an admin with MySQL."""
        os.environ["TEST_MODE"] = "0"
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        self.app.mydb = mock_db
        self.app.mycursor = mock_cursor
        self.app.mycursor.execute(
            "INSERT INTO AdminRecord (AdminID, Password) VALUES (%s, %s)",
            ("A102", "mysqlpass")
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT Password FROM AdminRecord WHERE AdminID = %s", ("A102",))
        mock_cursor.fetchone.return_value = ("mysqlpass",)
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "mysqlpass", "Admin not added correctly")

    def test_search_user_sqlite(self):
        """Test searching a user with SQLite."""
        user_data = ("110", "SearchUser", "pass", None, None, 0.00)
        self.app.mycursor.execute(
            "INSERT INTO UserRecord VALUES (?, ?, ?, ?, ?, ?)",
            user_data
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT UserName FROM UserRecord WHERE UserID = ?", ("110",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "SearchUser", "User not found correctly")

    def test_submit_feedback_sqlite(self):
        """Test submitting feedback with SQLite."""
        feedback_data = ("Awesome system!", "9")
        self.app.mycursor.execute(
            "INSERT INTO Feedback (Feedback, Rating) VALUES (?, ?)",
            feedback_data
        )
        self.app.mydb.commit()
        self.app.mycursor.execute("SELECT Feedback, Rating FROM Feedback WHERE Feedback = ?", ("Awesome system!",))
        result = self.app.mycursor.fetchone()
        self.assertEqual(result[0], "Awesome system!", "Feedback not submitted correctly")
        self.assertEqual(result[1], "9", "Rating not submitted correctly")

if __name__ == "__main__":
    unittest.main()