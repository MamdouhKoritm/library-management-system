 A Python-based desktop application for managing a library, built with Tkinter, MySQL, and bcrypt.

 ## Features
 - **Admin**: Add/delete books, manage users, view feedback.
 - **User**: Register, log in, search/issue/return books, submit feedback.
 - **Security**: Passwords hashed with bcrypt.
 - **Testing**: Unit tests with pytest.
 - **CI/CD**: GitHub Actions for automated testing.

 ## Setup
 1. **Prerequisites**:
    - Python 3.10
    - MySQL
    - Git

 2. **Clone Repository**:
    ```bash
    git clone https://github.com/MamdouhKoritm/library-management-system.git
    cd library-management-system
    ```

 3. **Set Up Virtual Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

 4. **Configure MySQL**:
    ```sql
    CREATE DATABASE library_db;
    CREATE USER 'libuser'@'localhost' IDENTIFIED BY 'libpass';
    GRANT ALL PRIVILEGES ON library_db.* TO 'libuser'@'localhost';
    ```
    Create `.env`:
    ```
    MYSQL_HOST=localhost
    MYSQL_USER=libuser
    MYSQL_PASSWORD=libpass
    MYSQL_DATABASE=library_db
    ```

 5. **Run Application**:
    ```bash
    python app.py
    ```

 6. **Run Tests**:
    ```bash
    pytest --cov=./
    ```

 ## CI/CD
 - GitHub Actions runs pytest on every push/pull request.
 - Check the **Actions** tab for test results.

 ## Contributing
 1. Fork the repository.
 2. Create a feature branch: `git checkout -b feature/your-feature`.
 3. Commit changes: `git commit -m "Add your feature"`.
 4. Push: `git push origin feature/your-feature`.
 5. Open a pull request.