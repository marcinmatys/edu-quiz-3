# EDU-QUIZ Backend

This is the FastAPI backend for the EDU-QUIZ application, handling all server-side logic and database operations.

## Setup

1. Make sure you have Python 3.8+ installed.

2. Create a virtual environment:
   ```
   cd backend
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

Start the development server with:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## Database

The application uses SQLite with SQLAlchemy ORM. The database file `edu-quiz.db` will be created automatically in the `backend` directory when you first run the application.

### Database Seeding

On startup, the application automatically:
- Creates all database tables if they don't exist
- Seeds the database with:
  - Predefined difficulty levels (Classes I-VIII)
  - Default admin user (username: `admin`, password: `admin123`)
  - Default student user (username: `student`, password: `student123`)

⚠️ **Note:** For production, you should change the default passwords!

## Project Structure

- `app/` - Main application package
  - `models/` - SQLAlchemy models defining the database schema
  - `schemas/` - Pydantic models for request/response validation
  - `routers/` - API endpoints grouped by functionality
  - `db/` - Database configuration and connection management
  - `core/` - Core functionality like configuration and security
  - `main.py` - Application entry point

## Development

### Adding a New Model

1. Create a new file in `app/models/`
2. Define your SQLAlchemy model
3. Import the model in `app/models/__init__.py`

### Adding a New API Endpoint

1. Create or update a router file in `app/routers/`
2. Add your endpoint functions
3. Include the router in `app/main.py`

## Running Tests

The application includes a comprehensive test suite for unit and integration testing. To run the tests:

1. Make sure you have installed the development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run all tests:
```bash
pytest
```

3. Run specific test categories:
```bash
# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run API tests only
pytest -m api
```

4. Run tests with coverage report:
```bash
pytest --cov=app
```

5. Generate HTML coverage report:
```bash
pytest --cov=app --cov-report=html
```

The coverage report will be available in the `htmlcov` directory.

## Rate Limiting

The API includes rate limiting for certain endpoints, particularly those that use external AI services:

- `/api/v1/quizzes`: 5 requests per minute with a burst capability of 5 requests 