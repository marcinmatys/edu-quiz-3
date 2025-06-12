import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from fastapi import status

from ...main import app
from ...services.quiz_service import QuizService
from ...services.ai_quiz_generator import AIGenerationError
from ...models.user import User

# Constants for testing
TEST_USER_ADMIN = {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "is_active": True
}

TEST_USER_STUDENT = {
    "id": 2,
    "username": "student",
    "role": "student",
    "is_active": True
}

TEST_QUIZ_DATA = {
    "topic": "Test Topic",
    "question_count": 5,
    "level_id": 1,
    "title": "Test Quiz"  # will be ignored as AI generates title
}

TEST_GENERATED_QUIZ = {
    "id": 1,
    "title": "Generated Quiz",
    "status": "draft",
    "level_id": 1,
    "creator_id": 1,
    "updated_at": "2023-06-15T12:00:00",
    "questions": [
        {
            "id": 1,
            "text": "Question 1?",
            "answers": [
                {"id": 1, "text": "Answer 1", "is_correct": True},
                {"id": 2, "text": "Answer 2", "is_correct": False},
                {"id": 3, "text": "Answer 3", "is_correct": False},
                {"id": 4, "text": "Answer 4", "is_correct": False}
            ]
        }
    ]
}

@pytest.fixture
def mock_get_current_active_admin():
    """Mock the get_current_active_admin dependency"""
    with patch("app.routers.quizzes.get_current_active_admin") as mock_admin:
        # Create a User object
        admin_user = MagicMock(spec=User)
        admin_user.id = TEST_USER_ADMIN["id"]
        admin_user.username = TEST_USER_ADMIN["username"]
        admin_user.role = TEST_USER_ADMIN["role"]
        admin_user.is_active = TEST_USER_ADMIN["is_active"]
        
        mock_admin.return_value = admin_user
        yield mock_admin

@pytest.fixture
def mock_quiz_service():
    """Mock the QuizService"""
    with patch.object(QuizService, "create_ai_quiz") as mock_create:
        yield mock_create

@pytest.mark.asyncio
async def test_create_quiz_success(mock_get_current_active_admin, mock_quiz_service):
    """Test successful quiz creation"""
    # Arrange
    mock_quiz_service.return_value = TEST_GENERATED_QUIZ
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/quizzes/", json=TEST_QUIZ_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == TEST_GENERATED_QUIZ["title"]
    assert response.json()["status"] == "draft"
    assert len(response.json()["questions"]) == 1
    
    # Verify service call
    mock_quiz_service.assert_called_once()
    args, kwargs = mock_quiz_service.call_args
    assert kwargs["quiz_data"].topic == TEST_QUIZ_DATA["topic"]
    assert kwargs["quiz_data"].question_count == TEST_QUIZ_DATA["question_count"]
    assert kwargs["quiz_data"].level_id == TEST_QUIZ_DATA["level_id"]

@pytest.mark.asyncio
async def test_create_quiz_validation_error(mock_get_current_active_admin, mock_quiz_service):
    """Test quiz creation with validation error"""
    # Arrange
    mock_quiz_service.side_effect = ValueError("Level with ID 999 not found")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/quizzes/", json=TEST_QUIZ_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Level with ID 999 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_quiz_ai_error(mock_get_current_active_admin, mock_quiz_service):
    """Test quiz creation with AI generation error"""
    # Arrange
    mock_quiz_service.side_effect = AIGenerationError("Failed to generate quiz")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/quizzes/", json=TEST_QUIZ_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Error generating quiz with AI" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_quiz_unexpected_error(mock_get_current_active_admin, mock_quiz_service):
    """Test quiz creation with unexpected error"""
    # Arrange
    mock_quiz_service.side_effect = Exception("Unexpected error")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/quizzes/", json=TEST_QUIZ_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_quiz_unauthorized():
    """Test quiz creation with unauthorized user (no token)"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/quizzes/", json=TEST_QUIZ_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_create_quiz_invalid_input():
    """Test quiz creation with invalid input data"""
    # Invalid data (missing required fields)
    invalid_data = {
        "topic": "Test Topic",
        # Missing question_count
        "level_id": 1
    }
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock the dependency to bypass authentication
        with patch("app.routers.quizzes.get_current_active_admin", return_value=TEST_USER_ADMIN):
            response = await client.post("/api/v1/quizzes/", json=invalid_data)
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 