print("Loading test_db_operations.py...")

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from io import StringIO
from datetime import datetime, timedelta
from decimal import Decimal  # Added for Decimal type
from app import mydb, mycursor  # Use the existing global mydb and mycursor

class TestDatabaseOperations(unittest.TestCase):
    def setUp(self):
        """Set up test environment with a fresh database state."""
        print("Starting setUp...")
        os.environ["TEST_MODE"] = "1"

        # Ensure the database connection is active
        if not mydb.is_connected():
            self.fail("Database connection is not active. Ensure app.py initializes the connection properly.")

        # Clear existing data for isolation
        try:
            print("Disabling foreign key checks...")
            mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            print("Clearing tables...")
            mycursor.execute("DELETE FROM BookRecord")
            print("BookRecord cleared.")
            mycursor.execute("DELETE FROM UserRecord")
            print("UserRecord cleared.")
            mycursor.execute("DELETE FROM AdminRecord")
            print("AdminRecord cleared.")
            mycursor.execute("DELETE FROM Feedback")
            print("Feedback cleared.")
            mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("Re-enabled foreign key checks.")
            mydb.commit()
            print("Tables cleared successfully.")
        except Exception as e:
            print(f"Error clearing tables in setUp: {e}")
            self.fail(f"Failed to clear tables in setUp: {e}")

        # Insert test data
        try:
            print("Inserting test data...")
            books = [
                ("B001", "To Kill a Mockingbird", "Harper Lee", "J.B. Lippincott", "Fiction", 10.99),
                ("B002", "1984", "George Orwell", "Secker & Warburg", "Fiction", 8.99)
            ]
            mycursor.executemany(
                "INSERT INTO BookRecord (BookID, BookName, Author, Publisher, Category, Price) VALUES (%s, %s, %s, %s, %s, %s)",
                books
            )
            print("Books inserted.")
            users = [
                ("101", "Kunal", "1234", None, None, 0.00)
            ]
            mycursor.executemany(
                "INSERT INTO UserRecord (UserID, UserName, Password, BookID, BorrowDate, Fine) VALUES (%s, %s, %s, %s, %s, %s)",
                users
            )
            print("Users inserted.")
            mydb.commit()
            print("Test data inserted successfully.")
        except Exception as e:
            print(f"Error inserting test data in setUp: {e}")
            self.fail(f"Failed to insert test data in setUp: {e}")

    def tearDown(self):
        """Clean up after tests."""
        print("Starting tearDown...")
        try:
            if mydb and mydb.is_connected():
                print("Cleaning database...")
                mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                mycursor.execute("DELETE FROM BookRecord")
                mycursor.execute("DELETE FROM UserRecord")
                mycursor.execute("DELETE FROM AdminRecord")
                mycursor.execute("DELETE FROM Feedback")
                mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                mydb.commit()
                print("Database cleaned successfully.")
                # Do not close mydb here since it's used globally and managed by app.py
        except Exception as e:
            print(f"Error during tearDown cleanup: {e}")
        if "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]
            print("TEST_MODE environment variable removed.")

    def test_database_connection(self):
        """Test if the database connection is active."""
        print("Running test_database_connection...")
        try:
            mycursor.execute("SELECT 1")
            result = mycursor.fetchone()
            self.assertEqual(result[0], 1, "Database connection test failed")
        except Exception as e:
            self.fail(f"Database connection test failed: {e}")

    def test_insert_book(self):
        """Test inserting a new book into BookRecord."""
        print("Running test_insert_book...")
        new_book = ("B003", "New Book", "New Author", "New Publisher", "Fiction", Decimal('15.99'))  # Convert price to Decimal
        try:
            mycursor.execute(
                "INSERT INTO BookRecord (BookID, BookName, Author, Publisher, Category, Price) VALUES (%s, %s, %s, %s, %s, %s)",
                new_book
            )
            mydb.commit()
            mycursor.execute("SELECT * FROM BookRecord WHERE BookID = %s", (new_book[0],))
            result = mycursor.fetchone()
            self.assertEqual(result, new_book, "Book insertion failed")
        except Exception as e:
            self.fail(f"Book insertion test failed: {e}")
        finally:
            mycursor.execute("DELETE FROM BookRecord WHERE BookID = %s", (new_book[0],))
            mydb.commit()

    def test_issue_book(self):
        """Test issuing a book to a user."""
        print("Running test_issue_book...")
        user_id = "101"
        book_id = "B001"
        borrow_date = "2025-05-09"
        try:
            mycursor.execute(
                "UPDATE UserRecord SET BookID = %s, BorrowDate = %s WHERE UserID = %s",
                (book_id, borrow_date, user_id)
            )
            mydb.commit()
            mycursor.execute("SELECT BookID, BorrowDate FROM UserRecord WHERE UserID = %s", (user_id,))
            result = mycursor.fetchone()
            self.assertEqual(result[0], book_id, "Book ID mismatch after issue")
            self.assertEqual(str(result[1]), borrow_date, "Borrow date mismatch after issue")
        except Exception as e:
            self.fail(f"Book issue test failed: {e}")
        finally:
            mycursor.execute("UPDATE UserRecord SET BookID = NULL, BorrowDate = NULL WHERE UserID = %s", (user_id,))
            mydb.commit()

    def test_return_book(self):
        """Test returning a book from a user."""
        print("Running test_return_book...")
        user_id = "101"
        book_id = "B001"
        borrow_date = "2025-04-25"
        fine = 0.00
        try:
            # Set up an issued book
            mycursor.execute(
                "UPDATE UserRecord SET BookID = %s, BorrowDate = %s, Fine = %s WHERE UserID = %s",
                (book_id, borrow_date, fine, user_id)
            )
            mydb.commit()

            # Return the book
            mycursor.execute(
                "UPDATE UserRecord SET BookID = NULL, BorrowDate = NULL WHERE UserID = %s",
                (user_id,)
            )
            mydb.commit()

            mycursor.execute("SELECT BookID, BorrowDate, Fine FROM UserRecord WHERE UserID = %s", (user_id,))
            result = mycursor.fetchone()
            self.assertIsNone(result[0], "Book ID should be NULL after return")
            self.assertIsNone(result[1], "Borrow date should be NULL after return")
            self.assertEqual(result[2], fine, "Fine should remain unchanged")
        except Exception as e:
            self.fail(f"Book return test failed: {e}")

    def test_overdue_fine_calculation(self):
        """Test overdue fine calculation."""
        print("Running test_overdue_fine_calculation...")
        user_id = "101"
        book_id = "B001"
        borrow_date = "2025-04-20"  # 19 days ago from 2025-05-09
        expected_fine = 5 * 0.50  # 5 days overdue
        try:
            mycursor.execute(
                "UPDATE UserRecord SET BookID = %s, BorrowDate = %s, Fine = 0.00 WHERE UserID = %s",
                (book_id, borrow_date, user_id)
            )
            mydb.commit()

            # Simulate check_overdue logic
            mycursor.execute("SELECT Fine FROM UserRecord WHERE UserID = %s", (user_id,))
            initial_fine = mycursor.fetchone()[0]
            self.assertEqual(initial_fine, 0.00, "Initial fine should be 0.00")

            # Manually calculate and update fine (mimicking check_overdue)
            current_date = datetime(2025, 5, 9)
            borrow_date_dt = datetime.strptime(borrow_date, "%Y-%m-%d")
            due_date = borrow_date_dt + timedelta(days=14)
            days_overdue = (current_date - due_date).days
            new_fine = days_overdue * 0.50
            mycursor.execute("UPDATE UserRecord SET Fine = %s WHERE UserID = %s", (new_fine, user_id))
            mydb.commit()

            mycursor.execute("SELECT Fine FROM UserRecord WHERE UserID = %s", (user_id,))
            result_fine = mycursor.fetchone()[0]
            self.assertAlmostEqual(result_fine, expected_fine, places=2, msg="Overdue fine calculation failed")
        except Exception as e:
            self.fail(f"Overdue fine calculation test failed: {e}")
        finally:
            mycursor.execute("UPDATE UserRecord SET BookID = NULL, BorrowDate = NULL, Fine = 0.00 WHERE UserID = %s", (user_id,))
            mydb.commit()

if __name__ == "__main__":
    print("Starting unittest.main()...")
    unittest.main()