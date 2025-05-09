import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import mysql.connector
import sys
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection
def init_db():
    """Initialize the database connection and create necessary tables."""
    try:
        if os.getenv("TEST_MODE") == "1":
            mydb = sqlite3.connect(":memory:")  # In-memory database for testing
            mycursor = mydb.cursor()
            placeholder = "?"
            is_sqlite = True
        else:
            mydb = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                passwd=os.getenv("DB_PASS", "@Mamdouh2"),
                database="Library"
            )
            mycursor = mydb.cursor()
            mycursor.execute("CREATE DATABASE IF NOT EXISTS Library")
            mycursor.execute("USE Library")
            placeholder = "%s"
            is_sqlite = False

        # Create BookRecord table
        table_check_query = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name='BookRecord'" if is_sqlite
            else "SELECT table_name FROM information_schema.tables WHERE table_schema = 'Library' AND table_name = 'BookRecord'"
        )
        mycursor.execute(table_check_query)
        if not mycursor.fetchone():
            create_query = (
                "CREATE TABLE BookRecord(" +
                "BookID TEXT PRIMARY KEY, " +
                "BookName TEXT, " +
                "Author TEXT, " +
                "Publisher TEXT, " +
                "Category TEXT, " +
                "Price REAL" +
                ")" if is_sqlite else
                "CREATE TABLE BookRecord(" +
                "BookID VARCHAR(255) PRIMARY KEY, " +
                "BookName VARCHAR(255), " +
                "Author VARCHAR(255), " +
                "Publisher VARCHAR(255), " +
                "Category VARCHAR(255), " +
                "Price DECIMAL(10,2)" +
                ")"
            )
            mycursor.execute(create_query)
            mydb.commit()

        # Verify table structure
        column_check_query = (
            "PRAGMA table_info(BookRecord)" if is_sqlite
            else "SELECT column_name FROM information_schema.columns WHERE table_schema = 'Library' AND table_name = 'BookRecord'"
        )
        mycursor.execute(column_check_query)
        columns = [col[1] if is_sqlite else col[0] for col in mycursor.fetchall()]
        if 'Category' not in columns:
            mycursor.execute("ALTER TABLE BookRecord ADD Category " + ("TEXT" if is_sqlite else "VARCHAR(255)"))
            mydb.commit()
        if 'Price' not in columns:
            mycursor.execute("ALTER TABLE BookRecord ADD Price " + ("REAL" if is_sqlite else "DECIMAL(10,2)"))
            mydb.commit()

        # Insert sample books
        mycursor.execute("SELECT COUNT(*) FROM BookRecord")
        if mycursor.fetchone()[0] == 0:
            books = [
                ("B001", "To Kill a Mockingbird", "Harper Lee", "J.B. Lippincott", "Fiction", 10.99),
                ("B002", "1984", "George Orwell", "Secker & Warburg", "Fiction", 8.99),
                ("B003", "Sapiens", "Yuval Noah Harari", "Harper", "Non-Fiction", 15.50),
                ("B004", "The Hobbit", "J.R.R. Tolkien", "Allen & Unwin", "Fantasy", 12.99),
                ("B005", "A Brief History of Time", "Stephen Hawking", "Bantam Books", "Science", 18.00),
                ("B006", "Pride and Prejudice", "Jane Austen", "T. Egerton", "Fiction", 7.99),
                ("B007", "The Catcher in the Rye", "J.D. Salinger", "Little, Brown", "Fiction", 9.50),
                ("B008", "The Great Gatsby", "F. Scott Fitzgerald", "Scribner", "Fiction", 8.00),
                ("B009", "Becoming", "Michelle Obama", "Crown", "Biography", 20.00),
                ("B010", "The Alchemist", "Paulo Coelho", "HarperOne", "Fiction", 10.00),
                ("B011", "Dune", "Frank Herbert", "Chilton Books", "Sci-Fi", 14.99),
                ("B012", "Educated", "Tara Westover", "Random House", "Biography", 16.50),
                ("B013", "The Da Vinci Code", "Dan Brown", "Doubleday", "Thriller", 12.00),
                ("B014", "Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Bloomsbury", "Fantasy", 13.99),
                ("B015", "The Road", "Cormac McCarthy", "Knopf", "Fiction", 11.50),
                ("B016", "Cosmos", "Carl Sagan", "Random House", "Science", 17.00),
                ("B017", "The Art of War", "Sun Tzu", "Various", "Philosophy", 5.99),
                ("B018", "The Name of the Wind", "Patrick Rothfuss", "DAW Books", "Fantasy", 14.00),
                ("B019", "Thinking, Fast and Slow", "Daniel Kahneman", "Farrar, Straus", "Psychology", 19.99),
                ("B020", "The Diary of a Young Girl", "Anne Frank", "Contact Publishing", "Biography", 9.99),
                ("B021", "Lord of the Flies", "William Golding", "Faber & Faber", "Fiction", 8.50),
                ("B022", "Guns, Germs, and Steel", "Jared Diamond", "W.W. Norton", "History", 16.00),
                ("B023", "The Shining", "Stephen King", "Doubleday", "Horror", 13.50),
                ("B024", "The Power of Habit", "Charles Duhigg", "Random House", "Self-Help", 12.99),
                ("B025", "Animal Farm", "George Orwell", "Secker & Warburg", "Fiction", 7.50),
                ("B026", "The Hunger Games", "Suzanne Collins", "Scholastic", "Sci-Fi", 11.99),
                ("B027", "A Game of Thrones", "George R.R. Martin", "Bantam Spectra", "Fantasy", 15.00),
                ("B028", "The Immortal Life of Henrietta Lacks", "Rebecca Skloot", "Crown", "Non-Fiction", 14.50),
                ("B029", "Brave New World", "Aldous Huxley", "Chatto & Windus", "Fiction", 9.00),
                ("B030", "The Origin of Species", "Charles Darwin", "John Murray", "Science", 20.50)
            ]
            query = "INSERT INTO BookRecord (BookID, BookName, Author, Publisher, Category, Price) VALUES (" + ",".join([placeholder]*6) + ")"
            mycursor.executemany(query, books)
            mydb.commit()
            print("Inserted 30 books into BookRecord table with prices.")

        # Create UserRecord table
        mycursor.execute(table_check_query.replace("BookRecord", "UserRecord"))
        if not mycursor.fetchone():
            create_query = (
                "CREATE TABLE UserRecord(" +
                "UserID TEXT PRIMARY KEY, " +
                "UserName TEXT, " +
                "Password TEXT, " +
                "BookID TEXT, " +
                "BorrowDate TEXT, " +
                "Fine REAL DEFAULT 0.00, " +
                "FOREIGN KEY (BookID) REFERENCES BookRecord(BookID)" +
                ")" if is_sqlite else
                "CREATE TABLE UserRecord(" +
                "UserID VARCHAR(255) PRIMARY KEY, " +
                "UserName VARCHAR(255), " +
                "Password VARCHAR(255), " +
                "BookID VARCHAR(255), " +
                "BorrowDate VARCHAR(255), " +
                "Fine DECIMAL(10,2) DEFAULT 0.00, " +
                "FOREIGN KEY (BookID) REFERENCES BookRecord(BookID)" +
                ")"
            )
            mycursor.execute(create_query)
            data = [("101", "Kunal", "1234", None, None, 0.00), 
                    ("102", "Vishal", "3050", None, None, 0.00), 
                    ("103", "Siddhesh", "5010", None, None, 0.00)]
            query = "INSERT INTO UserRecord VALUES (" + ",".join([placeholder]*6) + ")"
            mycursor.executemany(query, data)
            mydb.commit()
        else:
            mycursor.execute(column_check_query.replace("BookRecord", "UserRecord"))
            columns = [col[1] if is_sqlite else col[0] for col in mycursor.fetchall()]
            if 'BorrowDate' not in columns:
                mycursor.execute("ALTER TABLE UserRecord ADD BorrowDate " + ("TEXT" if is_sqlite else "VARCHAR(255)"))
                mydb.commit()
            if 'Fine' not in columns:
                mycursor.execute("ALTER TABLE UserRecord ADD Fine " + ("REAL DEFAULT 0.00" if is_sqlite else "DECIMAL(10,2) DEFAULT 0.00"))
                mydb.commit()

        # Create AdminRecord table
        mycursor.execute(table_check_query.replace("BookRecord", "AdminRecord"))
        if not mycursor.fetchone():
            create_query = (
                "CREATE TABLE AdminRecord(" +
                "AdminID TEXT PRIMARY KEY, " +
                "Password TEXT" +
                ")" if is_sqlite else
                "CREATE TABLE AdminRecord(" +
                "AdminID VARCHAR(255) PRIMARY KEY, " +
                "Password VARCHAR(255)" +
                ")"
            )
            mycursor.execute(create_query)
            data = [("Kunal1020", "123"), ("Siddesh510", "786"), ("Vishal305", "675")]
            query = "INSERT INTO AdminRecord VALUES (" + ",".join([placeholder]*2) + ")"
            mycursor.executemany(query, data)
            mydb.commit()

        # Create Feedback table
        mycursor.execute(table_check_query.replace("BookRecord", "Feedback"))
        if not mycursor.fetchone():
            create_query = (
                "CREATE TABLE Feedback(" +
                "Feedback TEXT PRIMARY KEY, " +
                "Rating TEXT" +
                ")" if is_sqlite else
                "CREATE TABLE Feedback(" +
                "Feedback VARCHAR(255) PRIMARY KEY, " +
                "Rating VARCHAR(255)" +
                ")"
            )
            mycursor.execute(create_query)
            mydb.commit()

        return mydb, mycursor, placeholder, is_sqlite

    except Exception as e:
        print(f"Unexpected error during database initialization: {e}")
        sys.exit(1)

# Main Application Window
class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("The Book Worm - Library Management System")
        self.geometry("800x600")
        self.mydb = None
        self.mycursor = None
        self.placeholder = "?"
        self.is_sqlite = True
        self.initialize_database()
        self.create_login_screen()

    def initialize_database(self):
        """Initialize the database connection within the application."""
        if not self.mydb:
            self.mydb, self.mycursor, self.placeholder, self.is_sqlite = init_db()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=50)

        tk.Label(frame, text="The Book Worm", font=("Arial", 20)).pack(pady=10)
        tk.Label(frame, text="Login", font=("Arial", 14)).pack(pady=10)

        tk.Button(frame, text="Admin Login", command=self.admin_login).pack(pady=5)
        tk.Button(frame, text="User Login", command=self.user_login).pack(pady=5)
        tk.Button(frame, text="Create User Account", command=self.create_user_account).pack(pady=5)
        tk.Button(frame, text="Exit", command=sys.exit).pack(pady=5)

    def admin_login(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=50)

        tk.Label(frame, text="Admin Login", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="Admin ID").pack()
        admin_id = tk.Entry(frame)
        admin_id.pack(pady=5)
        tk.Label(frame, text="Password").pack()
        password = tk.Entry(frame, show="*")
        password.pack(pady=5)

        attempts = [3]
        def try_login():
            start_time = time.time()
            attempts[0] -= 1
            query = f"SELECT Password FROM AdminRecord WHERE AdminID={self.placeholder}"
            try:
                self.mycursor.execute(query, (admin_id.get(),))
                result = self.mycursor.fetchone()
                if result and result[0] == password.get():
                    if time.time() - start_time > 2:
                        messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                    self.admin_menu()
                else:
                    messagebox.showerror("Error", f"Invalid credentials. {attempts[0]} attempts left.")
                    if attempts[0] == 0:
                        sys.exit()
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {e}")

        tk.Button(frame, text="Login", command=try_login).pack(pady=10)
        tk.Button(frame, text="Back", command=self.create_login_screen).pack(pady=5)

    def user_login(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=50)

        tk.Label(frame, text="User Login", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)
        tk.Label(frame, text="Password").pack()
        password = tk.Entry(frame, show="*")
        password.pack(pady=5)

        attempts = [3]
        def try_login():
            start_time = time.time()
            attempts[0] -= 1
            query = f"SELECT Password, UserID FROM UserRecord WHERE UserID={self.placeholder}"
            try:
                self.mycursor.execute(query, (user_id.get(),))
                result = self.mycursor.fetchone()
                if result and result[0] == password.get():
                    if time.time() - start_time > 2:
                        messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                    self.check_overdue(user_id.get())
                    self.user_menu()
                else:
                    messagebox.showerror("Error", f"Invalid credentials. {attempts[0]} attempts left.")
                    if attempts[0] == 0:
                        sys.exit()
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {e}")

        tk.Button(frame, text="Login", command=try_login).pack(pady=10)
        tk.Button(frame, text="Back", command=self.create_login_screen).pack(pady=5)

    def check_overdue(self, user_id):
        query = f"SELECT BookID, BorrowDate, Fine FROM UserRecord WHERE UserID={self.placeholder} AND BookID IS NOT NULL"
        try:
            self.mycursor.execute(query, (user_id,))
            result = self.mycursor.fetchone()
            if result:
                book_id, borrow_date, fine = result
                if borrow_date:
                    borrow_date = datetime.strptime(str(borrow_date), "%Y-%m-%d")
                    due_date = borrow_date + timedelta(days=14)
                    current_date = datetime.now()
                    if current_date > due_date:
                        days_overdue = (current_date - due_date).days
                        new_fine = days_overdue * 0.50
                        if new_fine > fine:
                            query = f"UPDATE UserRecord SET Fine = {self.placeholder} WHERE UserID = {self.placeholder}"
                            self.mycursor.execute(query, (new_fine, user_id))
                            self.mydb.commit()
                            messagebox.showwarning("Overdue Alert", f"Book ID {book_id} is overdue by {days_overdue} days. Fine updated to: ${new_fine}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check overdue: {e}")

    def create_user_account(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=50)

        tk.Label(frame, text="Create User Account", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)
        tk.Label(frame, text="User Name").pack()
        user_name = tk.Entry(frame)
        user_name.pack(pady=5)
        tk.Label(frame, text="Password").pack()
        password = tk.Entry(frame, show="*")
        password.pack(pady=5)

        def create_account():
            start_time = time.time()
            query = f"INSERT INTO UserRecord VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})"
            try:
                self.mycursor.execute(query, (user_id.get(), user_name.get(), password.get(), None, None, 0.00))
                self.mydb.commit()
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                messagebox.showinfo("Success", "Account created successfully!")
                self.create_login_screen()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create account: {e}")

        tk.Button(frame, text="Create Account", command=create_account).pack(pady=10)
        tk.Button(frame, text="Back", command=self.create_login_screen).pack(pady=5)

    def admin_menu(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=50)

        tk.Label(frame, text="Admin Menu", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame, text="Book Management", command=self.book_management).pack(pady=5)
        tk.Button(frame, text="User Management", command=self.user_management).pack(pady=5)
        tk.Button(frame, text="Admin Management", command=self.admin_management).pack(pady=5)
        tk.Button(frame, text="View Feedback", command=self.view_feedback).pack(pady=5)
        tk.Button(frame, text="Generate Reports", command=self.generate_reports).pack(pady=5)
        tk.Button(frame, text="Logout", command=self.create_login_screen).pack(pady=5)

    def user_menu(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=50)

        tk.Label(frame, text="User Menu", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame, text="Search Books", command=self.search_books).pack(pady=5)
        tk.Button(frame, text="Browse Books", command=self.browse_books).pack(pady=5)
        tk.Button(frame, text="Issue Book", command=self.issue_book).pack(pady=5)
        tk.Button(frame, text="Return Book", command=self.return_book).pack(pady=5)
        tk.Button(frame, text="View Issued Books", command=self.view_issued_books).pack(pady=5)
        tk.Button(frame, text="Submit Feedback", command=self.submit_feedback).pack(pady=5)
        tk.Button(frame, text="Logout", command=self.create_login_screen).pack(pady=5)

    def book_management(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Book Management", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame, text="Add Book", command=self.add_book).pack(pady=5)
        tk.Button(frame, text="Delete Book", command=self.delete_book).pack(pady=5)
        tk.Button(frame, text="View Books", command=self.view_books).pack(pady=5)
        tk.Button(frame, text="Back", command=self.admin_menu).pack(pady=5)

    def user_management(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="User Management", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame, text="Add User", command=self.add_user).pack(pady=5)
        tk.Button(frame, text="Remove User", command=self.remove_user).pack(pady=5)
        tk.Button(frame, text="View Users", command=self.view_users).pack(pady=5)
        tk.Button(frame, text="Apply Penalty", command=self.apply_penalty).pack(pady=5)
        tk.Button(frame, text="Back", command=self.admin_menu).pack(pady=5)

    def admin_management(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Admin Management", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame, text="Add Admin", command=self.add_admin).pack(pady=5)
        tk.Button(frame, text="View Admins", command=self.view_admins).pack(pady=5)
        tk.Button(frame, text="Back", command=self.admin_menu).pack(pady=5)

    def add_book(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Add Book", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="Book ID").pack()
        book_id = tk.Entry(frame)
        book_id.pack(pady=5)
        tk.Label(frame, text="Book Name").pack()
        book_name = tk.Entry(frame)
        book_name.pack(pady=5)
        tk.Label(frame, text="Author").pack()
        author = tk.Entry(frame)
        author.pack(pady=5)
        tk.Label(frame, text="Publisher").pack()
        publisher = tk.Entry(frame)
        publisher.pack(pady=5)
        tk.Label(frame, text="Category").pack()
        category = tk.Entry(frame)
        category.pack(pady=5)
        tk.Label(frame, text="Price ($)").pack()
        price = tk.Entry(frame)
        price.pack(pady=5)

        def save_book():
            start_time = time.time()
            query = f"INSERT INTO BookRecord (BookID, BookName, Author, Publisher, Category, Price) VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})"
            try:
                self.mycursor.execute(query, (book_id.get(), book_name.get(), author.get(), publisher.get(), category.get(), float(price.get())))
                self.mydb.commit()
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                messagebox.showinfo("Success", "Book added successfully!")
                self.book_management()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add book: {e}")

        tk.Button(frame, text="Save", command=save_book).pack(pady=10)
        tk.Button(frame, text="Back", command=self.book_management).pack(pady=5)

    def delete_book(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Delete Book", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="Book ID").pack()
        book_id = tk.Entry(frame)
        book_id.pack(pady=5)

        def delete():
            start_time = time.time()
            query = f"DELETE FROM BookRecord WHERE BookID = {self.placeholder}"
            try:
                self.mycursor.execute(query, (book_id.get(),))
                self.mydb.commit()
                if self.mycursor.rowcount == 0:
                    messagebox.showerror("Error", "Book ID not found.")
                else:
                    if time.time() - start_time > 2:
                        messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                    messagebox.showinfo("Success", "Book deleted successfully!")
                self.book_management()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete book: {e}")

        tk.Button(frame, text="Delete", command=delete).pack(pady=10)
        tk.Button(frame, text="Back", command=self.book_management).pack(pady=5)

    def view_books(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Book Records", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(frame, columns=("BookID", "Name", "Author", "Publisher", "Category", "Price", "IssuedBy", "UserID"), show="headings")
        tree.heading("BookID", text="Book ID")
        tree.heading("Name", text="Book Name")
        tree.heading("Author", text="Author")
        tree.heading("Publisher", text="Publisher")
        tree.heading("Category", text="Category")
        tree.heading("Price", text="Price ($)")
        tree.heading("IssuedBy", text="Issued By")
        tree.heading("UserID", text="User ID")
        tree.pack(fill="both", expand=True)

        query = ("SELECT BookRecord.BookID, BookRecord.BookName, BookRecord.Author, " +
                 "BookRecord.Publisher, BookRecord.Category, BookRecord.Price, " +
                 "UserRecord.UserName, UserRecord.UserID " +
                 "FROM BookRecord LEFT JOIN UserRecord ON BookRecord.BookID=UserRecord.BookID")
        try:
            self.mycursor.execute(query)
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No books found in the database.")
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch books: {e}")

        tk.Button(frame, text="Back", command=self.book_management).pack(pady=5)

    def add_user(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Add User", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)
        tk.Label(frame, text="User Name").pack()
        user_name = tk.Entry(frame)
        user_name.pack(pady=5)
        tk.Label(frame, text="Password").pack()
        password = tk.Entry(frame, show="*")
        password.pack(pady=5)

        def save_user():
            start_time = time.time()
            query = f"INSERT INTO UserRecord VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})"
            try:
                self.mycursor.execute(query, (user_id.get(), user_name.get(), password.get(), None, None, 0.00))
                self.mydb.commit()
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                messagebox.showinfo("Success", "User added successfully!")
                self.user_management()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add user: {e}")

        tk.Button(frame, text="Save", command=save_user).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_management).pack(pady=5)

    def remove_user(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Remove User", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)

        def remove():
            start_time = time.time()
            query = f"DELETE FROM UserRecord WHERE UserID = {self.placeholder}"
            try:
                self.mycursor.execute(query, (user_id.get(),))
                self.mydb.commit()
                if self.mycursor.rowcount == 0:
                    messagebox.showerror("Error", "User ID not found.")
                else:
                    if time.time() - start_time > 2:
                        messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                    messagebox.showinfo("Success", "User removed successfully!")
                self.user_management()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove user: {e}")

        tk.Button(frame, text="Remove", command=remove).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_management).pack(pady=5)

    def view_users(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="User Records", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(frame, columns=("UserID", "Name", "Password", "BookIssued", "BookID", "BorrowDate", "Fine"), show="headings")
        tree.heading("UserID", text="User ID")
        tree.heading("Name", text="User Name")
        tree.heading("Password", text="Password")
        tree.heading("BookIssued", text="Book Issued")
        tree.heading("BookID", text="Book ID")
        tree.heading("BorrowDate", text="Borrow Date")
        tree.heading("Fine", text="Fine ($)")
        tree.pack(fill="both", expand=True)

        query = ("SELECT UserRecord.UserID, UserRecord.UserName, UserRecord.Password, " +
                 "BookRecord.BookName, UserRecord.BookID, UserRecord.BorrowDate, UserRecord.Fine " +
                 "FROM UserRecord LEFT JOIN BookRecord ON UserRecord.BookID=BookRecord.BookID")
        try:
            self.mycursor.execute(query)
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No users found in the database.")
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch users: {e}")

        tk.Button(frame, text="Back", command=self.user_management).pack(pady=5)

    def apply_penalty(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Apply Penalty", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)
        tk.Label(frame, text="Penalty Amount").pack()
        penalty = tk.Entry(frame)
        penalty.pack(pady=5)

        def apply():
            start_time = time.time()
            query = f"SELECT Fine FROM UserRecord WHERE UserID = {self.placeholder}"
            try:
                self.mycursor.execute(query, (user_id.get(),))
                result = self.mycursor.fetchone()
                if result:
                    current_fine = result[0]
                    new_fine = current_fine + float(penalty.get())
                    update_query = f"UPDATE UserRecord SET Fine = {self.placeholder} WHERE UserID = {self.placeholder}"
                    self.mycursor.execute(update_query, (new_fine, user_id.get()))
                    self.mydb.commit()
                    if time.time() - start_time > 2:
                        messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                    messagebox.showinfo("Success", f"Penalty of ${penalty.get()} applied. Total fine: ${new_fine}")
                else:
                    messagebox.showerror("Error", "User ID not found.")
                self.user_management()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply penalty: {e}")

        tk.Button(frame, text="Apply", command=apply).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_management).pack(pady=5)

    def add_admin(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Add Admin", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="Admin ID").pack()
        admin_id = tk.Entry(frame)
        admin_id.pack(pady=5)
        tk.Label(frame, text="Password").pack()
        password = tk.Entry(frame, show="*")
        password.pack(pady=5)

        def save_admin():
            start_time = time.time()
            query = f"INSERT INTO AdminRecord VALUES ({self.placeholder}, {self.placeholder})"
            try:
                self.mycursor.execute(query, (admin_id.get(), password.get()))
                self.mydb.commit()
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                messagebox.showinfo("Success", "Admin added successfully!")
                self.admin_management()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add admin: {e}")

        tk.Button(frame, text="Save", command=save_admin).pack(pady=10)
        tk.Button(frame, text="Back", command=self.admin_management).pack(pady=5)

    def view_admins(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Admin Records", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(frame, columns=("AdminID", "Password"), show="headings")
        tree.heading("AdminID", text="Admin ID")
        tree.heading("Password", text="Password")
        tree.pack(fill="both", expand=True)

        try:
            self.mycursor.execute("SELECT * FROM AdminRecord")
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No admins found in the database.")
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch admins: {e}")

        tk.Button(frame, text="Back", command=self.admin_management).pack(pady=5)

    def search_books(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Search Books", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="Search by").pack()
        search_by = ttk.Combobox(frame, values=["Title", "Category"])
        search_by.pack(pady=5)
        tk.Label(frame, text="Search Term").pack()
        search_term = tk.Entry(frame)
        search_term.pack(pady=5)

        def perform_search():
            start_time = time.time()
            frame2 = tk.Frame(frame)
            frame2.pack(pady=10)
            tree = ttk.Treeview(frame2, columns=("BookID", "Name", "Author", "Publisher", "Category", "Price"), show="headings")
            tree.heading("BookID", text="Book ID")
            tree.heading("Name", text="Book Name")
            tree.heading("Author", text="Author")
            tree.heading("Publisher", text="Publisher")
            tree.heading("Category", text="Category")
            tree.heading("Price", text="Price ($)")
            tree.pack(fill="both", expand=True)

            search_field = {"Title": "BookName", "Category": "Category"}[search_by.get()]
            query = f"SELECT BookID, BookName, Author, Publisher, Category, Price FROM BookRecord WHERE {search_field} LIKE {self.placeholder}"
            try:
                self.mycursor.execute(query, ("%" + search_term.get() + "%",))
                rows = self.mycursor.fetchall()
                if not rows:
                    messagebox.showinfo("Info", "No books found matching your search criteria.")
                for row in rows:
                    tree.insert("", "end", values=row)
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to search books: {e}")

        tk.Button(frame, text="Search", command=perform_search).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_menu).pack(pady=5)

    def browse_books(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Browse Books", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(frame, columns=("BookID", "Name", "Author", "Publisher", "Category", "Price"), show="headings")
        tree.heading("BookID", text="Book ID")
        tree.heading("Name", text="Book Name")
        tree.heading("Author", text="Author")
        tree.heading("Publisher", text="Publisher")
        tree.heading("Category", text="Category")
        tree.heading("Price", text="Price ($)")
        tree.pack(fill="both", expand=True)

        try:
            self.mycursor.execute("SELECT BookID, BookName, Author, Publisher, Category, Price FROM BookRecord")
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No books available in the library. Please check database setup.")
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch books: {e}")

        tk.Button(frame, text="Back", command=self.user_menu).pack(pady=5)

    def issue_book(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Issue Book", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)

        tk.Label(frame, text="Select Book to Issue").pack()
        tree = ttk.Treeview(frame, columns=("BookID", "Name", "Author", "Publisher", "Category", "Price"), show="headings")
        tree.heading("BookID", text="Book ID")
        tree.heading("Name", text="Book Name")
        tree.heading("Author", text="Author")
        tree.heading("Publisher", text="Publisher")
        tree.heading("Category", text="Category")
        tree.heading("Price", text="Price ($)")
        tree.pack(fill="both", expand=True)

        try:
            query = ("SELECT BookID, BookName, Author, Publisher, Category, Price " +
                     "FROM BookRecord " +
                     "WHERE BookID NOT IN (SELECT BookID FROM UserRecord WHERE BookID IS NOT NULL)")
            self.mycursor.execute(query)
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No books available to issue.")
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch available books: {e}")

        def issue():
            start_time = time.time()
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a book to issue.")
                return
            book_id = tree.item(selected_item[0])["values"][0]
            try:
                query = f"SELECT BookID FROM UserRecord WHERE UserID={self.placeholder}"
                self.mycursor.execute(query, (user_id.get(),))
                result = self.mycursor.fetchone()
                if result and result[0]:
                    messagebox.showerror("Error", "You already have a book issued. Return it first.")
                    return
                query = f"SELECT UserID FROM UserRecord WHERE BookID={self.placeholder}"
                self.mycursor.execute(query, (book_id,))
                if self.mycursor.fetchone():
                    messagebox.showerror("Error", "Book is already issued.")
                    return
                borrow_date = datetime.now().strftime("%Y-%m-%d")
                query = f"UPDATE UserRecord SET BookID={self.placeholder}, BorrowDate={self.placeholder} WHERE UserID={self.placeholder}"
                self.mycursor.execute(query, (book_id, borrow_date, user_id.get()))
                self.mydb.commit()
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                messagebox.showinfo("Success", f"Book {book_id} issued successfully! Due by {due_date}")
                self.user_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to issue book: {e}")

        tk.Button(frame, text="Issue", command=issue).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_menu).pack(pady=5)

    def return_book(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Return Book", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)

        def return_book():
            start_time = time.time()
            query = f"SELECT BookID, BorrowDate, Fine FROM UserRecord WHERE UserID={self.placeholder} AND BookID IS NOT NULL"
            try:
                self.mycursor.execute(query, (user_id.get(),))
                result = self.mycursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "No book issued to this user.")
                    return
                book_id, borrow_date, fine = result
                if borrow_date:
                    borrow_date = datetime.strptime(str(borrow_date), "%Y-%m-%d")
                    due_date = borrow_date + timedelta(days=14)
                    current_date = datetime.now()
                    if current_date > due_date:
                        days_overdue = (current_date - due_date).days
                        new_fine = days_overdue * 0.50
                        if new_fine > fine:
                            query = f"UPDATE UserRecord SET Fine = {self.placeholder} WHERE UserID = {self.placeholder}"
                            self.mycursor.execute(query, (new_fine, user_id.get()))
                            self.mydb.commit()
                            fine = new_fine
                            messagebox.showwarning("Fine", f"Book was overdue by {days_overdue} days. Fine updated to: ${fine}")
                
                query = f"UPDATE UserRecord SET BookID={self.placeholder}, BorrowDate={self.placeholder} WHERE UserID={self.placeholder}"
                self.mycursor.execute(query, (None, None, user_id.get()))
                self.mydb.commit()
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                messagebox.showinfo("Success", f"Book {book_id} returned successfully! Fine paid: ${fine}")
                self.user_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to return book: {e}")

        tk.Button(frame, text="Return", command=return_book).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_menu).pack(pady=5)

    def view_issued_books(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Issued Books", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="User ID").pack()
        user_id = tk.Entry(frame)
        user_id.pack(pady=5)

        def show_issued():
            start_time = time.time()
            frame2 = tk.Frame(frame)
            frame2.pack(pady=10)
            tree = ttk.Treeview(frame2, columns=("UserID", "UserName", "BookID", "BookName", "BorrowDate", "Fine"), 
                               show="headings")
            tree.heading("UserID", text="User ID")
            tree.heading("UserName", text="User Name")
            tree.heading("BookID", text="Book ID")
            tree.heading("BookName", text="Book Name")
            tree.heading("BorrowDate", text="Borrow Date")
            tree.heading("Fine", text="Fine ($)")
            tree.pack(fill="both", expand=True)

            query = ("SELECT UserRecord.UserID, UserRecord.UserName, UserRecord.BookID, " +
                     "BookRecord.BookName, UserRecord.BorrowDate, UserRecord.Fine " +
                     "FROM UserRecord INNER JOIN BookRecord ON UserRecord.BookID=BookRecord.BookID " +
                     f"WHERE UserRecord.UserID={self.placeholder}")
            try:
                self.mycursor.execute(query, (user_id.get(),))
                rows = self.mycursor.fetchall()
                if not rows:
                    messagebox.showinfo("Info", "No books issued to this user.")
                for row in rows:
                    tree.insert("", "end", values=row)
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch issued books: {e}")

        tk.Button(frame, text="Show Issued Books", command=show_issued).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_menu).pack(pady=5)

    def submit_feedback(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Submit Feedback", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="Feedback").pack()
        feedback = tk.Entry(frame, width=50)
        feedback.pack(pady=5)
        tk.Label(frame, text="Rating (out of 10)").pack()
        rating = tk.Entry(frame)
        rating.pack(pady=5)

        def save_feedback():
            start_time = time.time()
            query = f"INSERT INTO Feedback VALUES ({self.placeholder}, {self.placeholder})"
            try:
                self.mycursor.execute(query, (feedback.get(), rating.get()))
                self.mydb.commit()
                if time.time() - start_time > 2:
                    messagebox.showwarning("Performance", "Response took longer than 2 seconds.")
                messagebox.showinfo("Success", "Feedback submitted successfully!")
                self.user_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to submit feedback: {e}")

        tk.Button(frame, text="Submit", command=save_feedback).pack(pady=10)
        tk.Button(frame, text="Back", command=self.user_menu).pack(pady=5)

    def view_feedback(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Feedback Records", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(frame, columns=("Feedback", "Rating"), show="headings")
        tree.heading("Feedback", text="Feedback")
        tree.heading("Rating", text="Rating")
        tree.pack(fill="both", expand=True)

        try:
            self.mycursor.execute("SELECT * FROM Feedback")
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No feedback available.")
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch feedback: {e}")

        tk.Button(frame, text="Back", command=self.admin_menu).pack(pady=5)

    def generate_reports(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Generate Reports", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame, text="Book Usage Report", command=self.book_usage_report).pack(pady=5)
        tk.Button(frame, text="Overdue Fines Report", command=self.overdue_fines_report).pack(pady=5)
        tk.Button(frame, text="Back", command=self.admin_menu).pack(pady=5)

    def book_usage_report(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Book Usage Report", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(frame, columns=("BookID", "BookName", "TimesIssued"), show="headings")
        tree.heading("BookID", text="Book ID")
        tree.heading("BookName", text="Book Name")
        tree.heading("TimesIssued", text="Times Issued")
        tree.pack(fill="both", expand=True)

        query = ("SELECT BookRecord.BookID, BookRecord.BookName, " +
                 "COUNT(UserRecord.BookID) as TimesIssued " +
                 "FROM BookRecord LEFT JOIN UserRecord " +
                 "ON BookRecord.BookID=UserRecord.BookID " +
                 "GROUP BY BookRecord.BookID, BookRecord.BookName")
        try:
            self.mycursor.execute(query)
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No book usage data available.")
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

        tk.Button(frame, text="Back", command=self.generate_reports).pack(pady=5)

    def overdue_fines_report(self):
        self.clear_window()
        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Overdue Fines Report", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(frame, columns=("UserID", "UserName", "BookID", "BookName", "DaysOverdue", "Fine"), 
                           show="headings")
        tree.heading("UserID", text="User ID")
        tree.heading("UserName", text="User Name")
        tree.heading("BookID", text="Book ID")
        tree.heading("BookName", text="Book Name")
        tree.heading("DaysOverdue", text="Days Overdue")
        tree.heading("Fine", text="Fine ($)")
        tree.pack(fill="both", expand=True)

        query = ("SELECT UserRecord.UserID, UserRecord.UserName, UserRecord.BookID, " +
                 "BookRecord.BookName, UserRecord.BorrowDate " +
                 "FROM UserRecord INNER JOIN BookRecord " +
                 "ON UserRecord.BookID=BookRecord.BookID")
        try:
            self.mycursor.execute(query)
            current_date = datetime.now()
            rows = self.mycursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No overdue books found.")
            for row in rows:
                borrow_date = row[4]
                if borrow_date:
                    borrow_date = datetime.strptime(str(borrow_date), "%Y-%m-%d")
                    due_date = borrow_date + timedelta(days=14)
                    if current_date > due_date:
                        days_overdue = (current_date - due_date).days
                        fine = days_overdue * 0.50
                        tree.insert("", "end", values=(row[0], row[1], row[2], row[3], days_overdue, str(fine)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

        tk.Button(frame, text="Back", command=self.generate_reports).pack(pady=5)

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()