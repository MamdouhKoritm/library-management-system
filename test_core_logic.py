import unittest
from datetime import datetime, timedelta
import sys
sys.path.append(".")
from app import mydb, mycursor

class TestCoreLogic(unittest.TestCase):
    def setUp(self):
        # Reset database for testing
        mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        mycursor.execute("DELETE FROM UserRecord")
        mycursor.execute("DELETE FROM BookRecord")
        mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        mydb.commit()
        
        # Insert test data
        books = [
            ("B001", "To Kill a Mockingbird", "Harper Lee", "J.B. Lippincott", "Fiction", 10.99),
            ("B002", "1984", "George Orwell", "Secker & Warburg", "Fiction", 8.99)
        ]
        mycursor.executemany(
            "INSERT INTO BookRecord (BookID, BookName, Author, Publisher, Category, Price) VALUES (%s, %s, %s, %s, %s, %s)",
            books
        )
        users = [
            ("101", "Kunal", "1234", None, None, 0.00)
        ]
        mycursor.executemany(
            "INSERT INTO UserRecord (UserID, UserName, Password, BookID, BorrowDate, Fine) VALUES (%s, %s, %s, %s, %s, %s)",
            users
        )
        mydb.commit()

    def tearDown(self):
        # Clean up after tests
        mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        mycursor.execute("DELETE FROM UserRecord")
        mycursor.execute("DELETE FROM BookRecord")
        mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        mydb.commit()

    def test_issue_book(self):
        # Test issuing a book
        user_id = "101"
        book_id = "B001"
        borrow_date = datetime.now().date()
        
        # Issue book
        mycursor.execute(
            "UPDATE UserRecord SET BookID=%s, BorrowDate=%s WHERE UserID=%s",
            (book_id, borrow_date, user_id)
        )
        mydb.commit()
        
        # Verify book is issued
        mycursor.execute("SELECT BookID, BorrowDate FROM UserRecord WHERE UserID=%s", (user_id,))
        result = mycursor.fetchone()
        self.assertEqual(result[0], book_id)
        self.assertEqual(str(result[1]), str(borrow_date))

    def test_return_book(self):
        # Setup: Issue a book first
        user_id = "101"
        book_id = "B001"
        borrow_date = datetime.now().date() - timedelta(days=10)
        
        mycursor.execute(
            "UPDATE UserRecord SET BookID=%s, BorrowDate=%s WHERE UserID=%s",
            (book_id, borrow_date, user_id)
        )
        mydb.commit()
        
        # Return book
        mycursor.execute(
            "UPDATE UserRecord SET BookID=NULL, BorrowDate=NULL WHERE UserID=%s",
            (user_id,)
        )
        mydb.commit()
        
        # Verify book is returned
        mycursor.execute("SELECT BookID, BorrowDate FROM UserRecord WHERE UserID=%s", (user_id,))
        result = mycursor.fetchone()
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

    def test_calculate_fine(self):
        # Setup: Issue an overdue book
        user_id = "101"
        book_id = "B001"
        borrow_date = datetime.now().date() - timedelta(days=16)  # 2 days overdue
        
        mycursor.execute(
            "UPDATE UserRecord SET BookID=%s, BorrowDate=%s WHERE UserID=%s",
            (book_id, borrow_date, user_id)
        )
        mydb.commit()
        
        # Calculate fine (2 days * $0.50 = $1.00)
        days_overdue = (datetime.now().date() - borrow_date).days - 14
        fine = days_overdue * 0.50
        
        # Update fine
        mycursor.execute(
            "UPDATE UserRecord SET Fine=%s WHERE UserID=%s",
            (fine, user_id)
        )
        mydb.commit()
        
        # Verify fine
        mycursor.execute("SELECT Fine FROM UserRecord WHERE UserID=%s", (user_id,))
        result = mycursor.fetchone()
        self.assertEqual(result[0], 1.00)

if __name__ == '__main__':
    unittest.main() 