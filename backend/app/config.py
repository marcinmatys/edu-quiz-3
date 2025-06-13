# Configuration settings for FastAPI backend
import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings:
    # Project info
    PROJECT_NAME = "EduQuiz API"
    VERSION = "0.1.0"
    DESCRIPTION = "API for the EduQuiz application"
    
    # Database settings
    DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/edu-quiz.db"
    
    # Security settings
    SECRET_KEY = "changethissecretkey"  # Change this in production!
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # CORS settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

settings = Settings()
