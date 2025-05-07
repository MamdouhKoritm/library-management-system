# Library Management System

A Python-based desktop application for managing a library, built with Tkinter and MySQL. The system supports admin and user functionalities, including book management, user management, book issuance, returns, fines, and feedback.

## Features
- **Admin Features**:
  - Manage books (add, delete, view)
  - Manage users (add, remove, view, apply penalties)
  - Manage admins (add, view)
  - View feedback
  - Generate reports (book usage, overdue fines)
- **User Features**:
  - Search and browse books
  - Issue and return books
  - View issued books
  - Submit feedback
- **Database**:
  - MySQL database with tables for books, users, admins, and feedback
  - Automatic initialization with sample data

## Prerequisites
- Python 3.8+
- MySQL Server
- Required Python packages (listed in `requirements.txt`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/library-management-system.git
   cd library-management-system
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up MySQL:
   - Ensure MySQL is running.
   - Update the database credentials in `db_connect.py` (default: host="localhost", user="root", passwd="@Mamdouh2").
4. Run the application:
   ```bash
   python app.py
   ```

## Project Structure
- `app.py`: Main application logic and Tkinter GUI.
- `db_connect.py`: Database connection and initialization.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Files to ignore in Git.
- `.github/workflows/ci.yml`: GitHub Actions CI/CD pipeline.

## CI/CD Pipeline
The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Lints the code using `flake8`.
- Runs tests (placeholder for future test implementation).
- Builds the project.

To enable CI/CD:
1. Push the code to a GitHub repository.
2. Ensure the workflow file is in the `.github/workflows/` directory.
3. The pipeline will run automatically on push or pull requests to the `main` branch.

## Database Setup
The application automatically creates a `Library` database and the following tables:
- `BookRecord`: Stores book details (BookID, BookName, Author, Publisher, Category, Price).
- `UserRecord`: Stores user details and borrowing info (UserID, UserName, Password, BookID, BorrowDate, Fine).
- `AdminRecord`: Stores admin credentials (AdminID, Password).
- `Feedback`: Stores user feedback (Feedback, Rating).

Sample data is inserted during the first run if the tables are empty.

## Usage
- **Admin Login**: Use AdminID (e.g., "Kunal1020") and Password (e.g., "123").
- **User Login**: Use UserID (e.g., "101") and Password (e.g., "1234").
- **Create User Account**: Register new users via the login screen.
- **Exit**: Closes the application.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

## License
This project is licensed under the MIT License.