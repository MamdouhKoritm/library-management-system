import mysql.connector
import sys
import bcrypt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def init_db():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            passwd=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME")
        )
        mycursor = mydb.cursor()
        
        # Create database if it doesn't exist
        mycursor.execute("CREATE DATABASE IF NOT EXISTS Library")
        mycursor.execute("USE Library")

        # Create BookRecord table
        mycursor.execute("SHOW TABLES LIKE 'BookRecord'")
        if not mycursor.fetchone():
            mycursor.execute("CREATE TABLE BookRecord(" +
                             "BookID varchar(10) PRIMARY KEY, " +
                             "BookName varchar(50), " +
                             "Author varchar(30), " +
                             "Publisher varchar(30), " +
                             "Category varchar(20), " +
                             "Price DECIMAL(10,2)" +
                             ")")
            mydb.commit()

        # Verify and update table structure
        mycursor.execute("SHOW COLUMNS FROM BookRecord LIKE 'Category'")
        if not mycursor.fetchone():
            mycursor.execute("ALTER TABLE BookRecord ADD COLUMN Category varchar(20)")
            mydb.commit()
        
        mycursor.execute("SHOW COLUMNS FROM BookRecord LIKE 'Price'")
        if not mycursor.fetchone():
            mycursor.execute("ALTER TABLE BookRecord ADD COLUMN Price DECIMAL(10,2)")
            mydb.commit()
        
        mycursor.execute("SHOW COLUMNS FROM BookRecord LIKE 'BookName'")
        bookname_result = mycursor.fetchone()
        if bookname_result and bookname_result[1] != 'varchar(50)':
            mycursor.execute("ALTER TABLE BookRecord MODIFY COLUMN BookName varchar(50)")
            mydb.commit()

        # Insert initial books if table is empty
        mycursor.execute("SELECT COUNT(*) FROM BookRecord")
        count_result = mycursor.fetchone()
        if count_result and count_result[0] == 0:
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
            query = "INSERT INTO BookRecord (BookID, BookName, Author, Publisher, Category, Price) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.executemany(query, books)
            mydb.commit()
            print("Inserted 30 books into BookRecord table with prices.")

        # Create UserRecord table
        mycursor.execute("SHOW TABLES LIKE 'UserRecord'")
        if not mycursor.fetchone():
            mycursor.execute("CREATE TABLE UserRecord(" +
                             "UserID varchar(10) PRIMARY KEY, " +
                             "UserName varchar(20), " +
                             "Password varchar(255), " +  # Increased length for hashed passwords
                             "BookID varchar(10), " +
                             "BorrowDate date, " +
                             "Fine DECIMAL(10,2) DEFAULT 0.00, " +
                             "FOREIGN KEY (BookID) REFERENCES BookRecord(BookID)" +
                             ")")
            # Hash initial user passwords
            users = [
                ("101", "Kunal", "1234", None, None, 0.00),
                ("102", "Vishal", "3050", None, None, 0.00),
                ("103", "Siddhesh", "5010", None, None, 0.00)
            ]
            hashed_users = [
                (uid, uname, bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), bid, bdate, fine)
                for uid, uname, pwd, bid, bdate, fine in users
            ]
            query = "INSERT INTO UserRecord VALUES(%s, %s, %s, %s, %s, %s)"
            mycursor.executemany(query, hashed_users)
            mydb.commit()
        else:
            mycursor.execute("SHOW COLUMNS FROM UserRecord LIKE 'BorrowDate'")
            if not mycursor.fetchone():
                mycursor.execute("ALTER TABLE UserRecord ADD BorrowDate DATE")
                mydb.commit()
            mycursor.execute("SHOW COLUMNS FROM UserRecord LIKE 'Fine'")
            if not mycursor.fetchone():
                mycursor.execute("ALTER TABLE UserRecord ADD Fine DECIMAL(10,2) DEFAULT 0.00")
                mydb.commit()
            mycursor.execute("SHOW COLUMNS FROM UserRecord LIKE 'Password'")
            password_result = mycursor.fetchone()
            if password_result and password_result[1] != 'varchar(255)':
                mycursor.execute("ALTER TABLE UserRecord MODIFY COLUMN Password varchar(255)")
                mydb.commit()

        # Create AdminRecord table
        mycursor.execute("SHOW TABLES LIKE 'AdminRecord'")
        if not mycursor.fetchone():
            mycursor.execute("CREATE TABLE AdminRecord(" +
                             "AdminID varchar(10) PRIMARY KEY, " +
                             "Password varchar(255)" +  # Increased length for hashed passwords
                             ")")
            # Hash initial admin passwords
            admins = [
                ("Kunal1020", "123"),
                ("Siddesh510", "786"),
                ("Vishal305", "675")
            ]
            hashed_admins = [
                (aid, bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
                for aid, pwd in admins
            ]
            query = "INSERT INTO AdminRecord VALUES(%s, %s)"
            mycursor.executemany(query, hashed_admins)
            mydb.commit()
        else:
            mycursor.execute("SHOW COLUMNS FROM AdminRecord LIKE 'Password'")
            password_result = mycursor.fetchone()
            if password_result and password_result[1] != 'varchar(255)':
                mycursor.execute("ALTER TABLE AdminRecord MODIFY COLUMN Password varchar(255)")
                mydb.commit()

        # Create Feedback table
        mycursor.execute("SHOW TABLES LIKE 'Feedback'")
        if not mycursor.fetchone():
            mycursor.execute("CREATE TABLE Feedback(" +
                             "Feedback varchar(100) PRIMARY KEY, " +
                             "Rating varchar(10)" +
                             ")")
            mydb.commit()

        return mydb, mycursor

    except mysql.connector.Error as e:
        print("Database connection failed: " + str(e))
        sys.exit(1)
    except Exception as e:
        print("Unexpected error during database initialization: " + str(e))
        sys.exit(1)