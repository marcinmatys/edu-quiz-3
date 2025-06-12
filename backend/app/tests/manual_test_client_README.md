# Quiz API Manual Test Client

This is a simple HTTP client for manually testing the Quiz API endpoints of the EduQuiz application.

## Requirements

- Python 3.7+
- httpx library (`pip install httpx`)

## Usage

1. Make sure the EduQuiz backend server is running
2. Run the client:

```powershell
# Navigate to the backend directory
cd backend

# Run the client
python -m app.tests.manual_test_client

# Or with credentials as command line arguments
python -m app.tests.manual_test_client username password
```

## Features

The client provides a simple menu-driven interface to:

1. **Get all quizzes** - Retrieves a list of all quizzes
2. **Create a new quiz** - Creates a new quiz with AI-generated questions
3. **Get quiz by ID** - Retrieves a specific quiz by its ID
4. **Exit** - Exit the application

## Authentication

The client requires authentication with a valid admin account. You can provide credentials:

- As command line arguments when running the script
- By entering them when prompted

## Example Flow

1. Run the client and log in with admin credentials
2. Choose option 2 to create a new quiz
3. Enter quiz details (topic, question count, and level ID)
4. The API will return the created quiz with AI-generated questions
5. Use option 1 to view all quizzes or option 3 to get the details of a specific quiz

## Notes

- The API endpoint requires admin privileges for creating quizzes
- Question count must be between 5 and 20
- Quiz generation may take some time depending on the AI service performance 