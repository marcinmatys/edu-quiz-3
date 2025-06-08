# Viewing SQLite Database Tables and Content

This document outlines several methods to view and interact with the SQLite database for the EDU-QUIZ application.

## Option 1: Using DB Browser for SQLite (GUI Tool)

DB Browser for SQLite is a visual tool that provides an easy way to view and edit SQLite databases.

1. **Download and Install**:
   - Download from [https://sqlitebrowser.org/dl/](https://sqlitebrowser.org/dl/)
   - Choose the appropriate version for your Windows system
   - Run the installer

2. **Open Your Database**:
   - Launch DB Browser for SQLite
   - Click "Open Database" and navigate to your project's `/backend` folder
   - Select the `edu-quiz.db` file

3. **Explore the Database**:
   - "Database Structure" tab: View all tables and their schemas
   - "Browse Data" tab: Browse and edit data in tables
   - "Execute SQL" tab: Run custom SQL queries

## Option 2: Using SQLite CLI (Command Line)

The SQLite command-line interface provides direct access to your database.

1. **Download SQLite Tools**:
   - Download from [https://www.sqlite.org/download.html](https://www.sqlite.org/download.html)
   - Look for "Precompiled Binaries for Windows" section
   - Download the "sqlite-tools" ZIP file (e.g., `sqlite-tools-win32-x86-3450200.zip`)

2. **Extract and Set Up**:
   - Extract the ZIP file to a location on your computer (e.g., `C:\sqlite`)
   - Add the folder to your Windows PATH environment variable:
     - Search for "Edit environment variables" in Windows
     - Edit the PATH variable and add the folder path

3. **Using the CLI**:
   - Open PowerShell or Command Prompt
   - Navigate to your backend directory
   - Run: `sqlite3 edu-quiz.db`

4. **Useful Commands**:
   - `.tables` - List all tables
   - `.schema tablename` - Show the structure of a specific table
   - `SELECT * FROM tablename;` - View all data in a table
   - `.exit` or `.quit` - Exit the SQLite CLI

## Option 3: Using the Python Script (view_db.py)

A custom Python script is included in the backend directory to provide an interactive view of the database.

1. **Run the Script**:
   ```
   cd backend
   python view_db.py
   ```

2. **Features**:
   - List all tables in the database
   - View the schema (structure) of any table
   - Browse the content of any table
   - Interactive menu-driven interface

## Option 4: Using FastAPI Debug Endpoints

The application includes built-in API endpoints for viewing database information during development.

1. **Start the Server**:
   ```
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Access the Endpoints**:
   - List all tables: [http://localhost:8000/debug/tables](http://localhost:8000/debug/tables)
   - View schema: [http://localhost:8000/debug/schema/{table_name}](http://localhost:8000/debug/schema/users)
   - View data: [http://localhost:8000/debug/data/{table_name}](http://localhost:8000/debug/data/users)
   - View all users: [http://localhost:8000/debug/users](http://localhost:8000/debug/users)
   - View all levels: [http://localhost:8000/debug/levels](http://localhost:8000/debug/levels)
   - View all quizzes: [http://localhost:8000/debug/quizzes](http://localhost:8000/debug/quizzes)
   - View quiz details: [http://localhost:8000/debug/quiz/{quiz_id}](http://localhost:8000/debug/quiz/1)

3. **API Documentation**:
   - Interactive Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Option 5: Programmatically Using SQLAlchemy

You can also query the database directly in Python code using SQLAlchemy:

```python
from app.db import SessionLocal
from app.models import User, Level, Quiz, Question, Answer, Result

# Create a database session
db = SessionLocal()

try:
    # Example: Query all users
    users = db.query(User).all()
    for user in users:
        print(f"User: {user.username}, Role: {user.role}")
    
    # Example: Query all levels
    levels = db.query(Level).all()
    for level in levels:
        print(f"Level: {level.code} - {level.description}")
        
    # Example: Query quizzes with their questions and answers
    quizzes = db.query(Quiz).all()
    for quiz in quizzes:
        print(f"Quiz: {quiz.title} (Status: {quiz.status})")
        for question in quiz.questions:
            print(f"  Question: {question.text}")
            for answer in question.answers:
                correct = "✓" if answer.is_correct else "✗"
                print(f"    Answer: {answer.text} {correct}")
finally:
    db.close()
```

## Security Note

The debug endpoints and the view_db.py script are meant for development purposes only. Make sure to:

1. Remove or disable the debug endpoints before deploying to production
2. Keep your database file secure and regularly backed up
3. Use proper authentication in your application to protect sensitive data

For production environments, consider using a more robust database solution like PostgreSQL. 