import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import sys
import time
sys.path.append(".")
from app import LibraryApp, mydb, mycursor

class TestGuiOperations(unittest.TestCase):
    def setUp(self):
        # Initialize the app
        self.app = LibraryApp()
        # Use the global mydb and mycursor, but reset them for testing
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
        # Helper to find widgets recursively
        def find_widget(parent, widget_type, text=None, preceding_label_text=None, depth=0):
            children = parent.winfo_children()
            for i, widget in enumerate(children):
                # Direct match for widgets with a text property (e.g., Button, Label)
                if isinstance(widget, widget_type) and (text is None or (hasattr(widget, 'cget') and widget.cget('text') == text)):
                    return widget
                # Special case for Entry: find by preceding Label with matching text
                if preceding_label_text and isinstance(widget, tk.Label) and widget.cget('text') == preceding_label_text:
                    # Look for the next Entry widget
                    for j in range(i + 1, len(children)):
                        if isinstance(children[j], widget_type):
                            return children[j]
                # Recursively search deeper
                if depth < 5:
                    found = find_widget(widget, widget_type, text, preceding_label_text, depth + 1)
                    if found:
                        return found
            return None
        self.find_widget = find_widget

    def tearDown(self):
        try:
            self.app.update()
            self.app.update_idletasks()
            mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            mycursor.execute("DELETE FROM UserRecord")
            mycursor.execute("DELETE FROM BookRecord")
            mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            mydb.commit()
            self.app.destroy()
        except Exception as e:
            print(f"Error during tearDown: {e}")

    @patch('app.messagebox')
    @patch('app.datetime')
    def test_issue_book_success(self, mock_datetime, mock_messagebox):
        # Mock current date
        mock_date = datetime(2025, 5, 9)
        mock_datetime.now.return_value = mock_date
        mock_datetime.strptime = datetime.strptime
        due_date = (mock_date + timedelta(days=14)).strftime("%Y-%m-%d")

        # Simulate issuing a book
        self.app.issue_book()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        frame = self.app.winfo_children()[0]
        user_id_entry = self.find_widget(frame, tk.Entry, preceding_label_text="User ID")
        self.assertIsNotNone(user_id_entry, "User ID Entry widget not found")
        user_id_entry.delete(0, tk.END)
        user_id_entry.insert(0, "101")
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        tree = self.find_widget(frame, ttk.Treeview)
        self.assertIsNotNone(tree, "Treeview widget not found")
        tree.selection_set(tree.get_children()[0])
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        issue_button = self.find_widget(frame, tk.Button, text="Issue")
        self.assertIsNotNone(issue_button, "Issue button not found")
        issue_button.invoke()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)

        # Check for error messages
        if mock_messagebox.showerror.called:
            self.fail(f"Unexpected error message: {mock_messagebox.showerror.call_args}")
        # Verify database state
        mycursor.execute("SELECT BookID, BorrowDate FROM UserRecord WHERE UserID=%s", ("101",))
        result = mycursor.fetchone()
        self.assertEqual(result[0], "B001")
        self.assertEqual(str(result[1]), "2025-05-09")
        mock_messagebox.showinfo.assert_called_with(
            "Success", f"Book B001 issued successfully! Due by {due_date}"
        )

    @patch('app.messagebox')
    @patch('app.datetime')
    def test_issue_book_already_issued(self, mock_datetime, mock_messagebox):
        # Mock current date
        mock_date = datetime(2025, 5, 9)
        mock_datetime.now.return_value = mock_date
        mock_datetime.strptime = datetime.strptime

        # Set up user with an issued book
        mycursor.execute("UPDATE UserRecord SET BookID=%s, BorrowDate=%s WHERE UserID=%s",
                         ("B001", "2025-05-09", "101"))
        mydb.commit()

        # Simulate issuing another book
        self.app.issue_book()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        frame = self.app.winfo_children()[0]
        user_id_entry = self.find_widget(frame, tk.Entry, preceding_label_text="User ID")
        self.assertIsNotNone(user_id_entry, "User ID Entry widget not found")
        user_id_entry.delete(0, tk.END)
        user_id_entry.insert(0, "101")
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        tree = self.find_widget(frame, ttk.Treeview)
        self.assertIsNotNone(tree, "Treeview widget not found")
        tree.selection_set(tree.get_children()[0])
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        issue_button = self.find_widget(frame, tk.Button, text="Issue")
        self.assertIsNotNone(issue_button, "Issue button not found")
        issue_button.invoke()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)

        # Verify error message
        mock_messagebox.showerror.assert_called_with(
            "Error", "You already have a book issued. Return it first."
        )

    @patch('app.messagebox')
    @patch('app.datetime')
    def test_return_book_success(self, mock_datetime, mock_messagebox):
        # Mock current date
        mock_date = datetime(2025, 5, 9)
        mock_datetime.now.return_value = mock_date
        mock_datetime.strptime = datetime.strptime

        # Set up user with an issued book
        mycursor.execute("UPDATE UserRecord SET BookID=%s, BorrowDate=%s, Fine=%s WHERE UserID=%s",
                         ("B001", "2025-04-25", 0.00, "101"))
        mydb.commit()

        # Simulate returning a book
        self.app.return_book()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        frame = self.app.winfo_children()[0]
        user_id_entry = self.find_widget(frame, tk.Entry, preceding_label_text="User ID")
        self.assertIsNotNone(user_id_entry, "User ID Entry widget not found")
        user_id_entry.delete(0, tk.END)
        user_id_entry.insert(0, "101")
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        return_button = self.find_widget(frame, tk.Button, text="Return")
        self.assertIsNotNone(return_button, "Return button not found")
        return_button.invoke()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)

        # Check for error messages
        if mock_messagebox.showerror.called:
            self.fail(f"Unexpected error message: {mock_messagebox.showerror.call_args}")
        # Verify database state
        mycursor.execute("SELECT BookID, BorrowDate, Fine FROM UserRecord WHERE UserID=%s", ("101",))
        result = mycursor.fetchone()
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        self.assertEqual(result[2], 0.00)
        mock_messagebox.showinfo.assert_called_with(
            "Success", "Book B001 returned successfully! Fine paid: $0.00"
        )

    @patch('app.messagebox')
    @patch('app.datetime')
    def test_return_book_overdue(self, mock_datetime, mock_messagebox):
        # Mock current date
        mock_date = datetime(2025, 5, 9)
        mock_datetime.now.return_value = mock_date
        mock_datetime.strptime = datetime.strptime

        # Set up user with an overdue book
        mycursor.execute("UPDATE UserRecord SET BookID=%s, BorrowDate=%s, Fine=%s WHERE UserID=%s",
                         ("B001", "2025-04-20", 0.00, "101"))
        mydb.commit()

        # Simulate returning a book
        self.app.return_book()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        frame = self.app.winfo_children()[0]
        user_id_entry = self.find_widget(frame, tk.Entry, preceding_label_text="User ID")
        self.assertIsNotNone(user_id_entry, "User ID Entry widget not found")
        user_id_entry.delete(0, tk.END)
        user_id_entry.insert(0, "101")
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        return_button = self.find_widget(frame, tk.Button, text="Return")
        self.assertIsNotNone(return_button, "Return button not found")
        return_button.invoke()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)

        # Verify fine calculation (5 days overdue at $0.50/day = $2.50)
        days_overdue = 5  # 2025-04-20 + 14 days = 2025-05-04, then 2025-05-09 - 2025-05-04 = 5 days
        expected_fine = days_overdue * 0.50
        mock_messagebox.showwarning.assert_called_with(
            "Fine", f"Book was overdue by {days_overdue} days. Fine updated to: ${expected_fine}"
        )
        # Verify database state
        mycursor.execute("SELECT BookID, BorrowDate, Fine FROM UserRecord WHERE UserID=%s", ("101",))
        result = mycursor.fetchone()
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        self.assertAlmostEqual(float(result[2]), expected_fine, places=2)
        mock_messagebox.showinfo.assert_called_with(
            "Success", f"Book B001 returned successfully! Fine paid: ${expected_fine}"
        )

    @patch('app.messagebox')
    @patch('app.datetime')
    def test_view_issued_books_success(self, mock_datetime, mock_messagebox):
        # Mock current date
        mock_date = datetime(2025, 5, 9)
        mock_datetime.now.return_value = mock_date
        mock_datetime.strptime = datetime.strptime

        # Set up user with an issued book
        mycursor.execute("UPDATE UserRecord SET BookID=%s, BorrowDate=%s, Fine=%s WHERE UserID=%s",
                         ("B001", "2025-04-25", 0.00, "101"))
        mydb.commit()

        # Simulate viewing issued books
        self.app.view_issued_books()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        frame = self.app.winfo_children()[0]
        user_id_entry = self.find_widget(frame, tk.Entry, preceding_label_text="User ID")
        self.assertIsNotNone(user_id_entry, "User ID Entry widget not found")
        user_id_entry.delete(0, tk.END)
        user_id_entry.insert(0, "101")
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)
        show_button = self.find_widget(frame, tk.Button, text="Show Issued Books")
        self.assertIsNotNone(show_button, "Show Issued Books button not found")
        show_button.invoke()
        self.app.update()
        self.app.update_idletasks()
        time.sleep(0.1)

        # Check for error messages
        if mock_messagebox.showerror.called:
            self.fail(f"Unexpected error message: {mock_messagebox.showerror.call_args}")
        # Find the Treeview widget to verify displayed data
        tree = self.find_widget(frame, ttk.Treeview)
        self.assertIsNotNone(tree, "Treeview widget not found")
        items = tree.get_children()
        self.assertEqual(len(items), 1, "Expected exactly one issued book to be displayed")
        displayed_values = tree.item(items[0])["values"]
        # Adjust expected_values to match the actual data type returned by the database driver
        expected_values = (101, "Kunal", "B001", "To Kill a Mockingbird", "2025-04-25", "0.00")
        self.assertEqual(tuple(displayed_values), expected_values, "Displayed issued book data does not match expected values")

if __name__ == '__main__':
    unittest.main()