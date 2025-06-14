import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from fastapi import status
from typing import List

from ...main import app
from ...services.quiz_service import QuizService
from ...services.ai_quiz_generator import AIGenerationError
from ...models.user import User
from ...schemas.quiz import QuizReadList, LastResult

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

TEST_QUIZ_LIST = [
    {
        "id": 1,
        "title": "Published Quiz",
        "status": "published",
        "level_id": 1,
        "creator_id": 1,
        "updated_at": "2023-06-15T12:00:00",
        "question_count": 10,
        "last_result": None
    },
    {
        "id": 2,
        "title": "Draft Quiz",
        "status": "draft",
        "level_id": 2,
        "creator_id": 1,
        "updated_at": "2023-06-16T12:00:00",
        "question_count": 5,
        "last_result": None
    }
]

TEST_QUIZ_LIST_STUDENT = [
    {
        "id": 1,
        "title": "Published Quiz",
        "status": "published",
        "level_id": 1,
        "creator_id": 1,
        "updated_at": "2023-06-15T12:00:00",
        "question_count": 10,
        "last_result": {
            "score": 8,
            "max_score": 10
        }
    }
]

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
def mock_get_current_active_user():
    """Mock the get_current_active_user dependency"""
    with patch("app.routers.quizzes.get_current_active_user") as mock_user:
        yield mock_user

@pytest.fixture
def mock_quiz_service():
    """Mock the QuizService"""
    with patch.object(QuizService, "create_ai_quiz") as mock_create:
        yield mock_create

@pytest.fixture
def mock_get_quizzes():
    """Mock the get_quizzes method of QuizService"""
    with patch.object(QuizService, "get_quizzes") as mock_get:
        yield mock_get

@pytest.fixture
def mock_get_quiz_by_id():
    """Mock the get_quiz_by_id method of QuizService"""
    with patch.object(QuizService, "get_quiz_by_id") as mock_get:
        yield mock_get

@pytest.mark.asyncio
async def test_list_quizzes_admin_success(mock_get_current_active_user, mock_get_quizzes):
    """Test successful quizzes listing as admin"""
    # Arrange
    admin_user = MagicMock(spec=User)
    admin_user.id = TEST_USER_ADMIN["id"]
    admin_user.username = TEST_USER_ADMIN["username"]
    admin_user.role = TEST_USER_ADMIN["role"]
    admin_user.is_active = TEST_USER_ADMIN["is_active"]
    
    mock_get_current_active_user.return_value = admin_user
    
    # Create QuizReadList objects
    quiz_list = [QuizReadList.model_validate(quiz) for quiz in TEST_QUIZ_LIST]
    mock_get_quizzes.return_value = quiz_list
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Published Quiz"
    assert response.json()[1]["title"] == "Draft Quiz"
    
    # Verify service call
    mock_get_quizzes.assert_called_once()
    args, kwargs = mock_get_quizzes.call_args
    assert kwargs["sort_by"] == "level"  # Default value
    assert kwargs["order"] == "asc"  # Default value
    assert kwargs["status"] is None  # Default value

@pytest.mark.asyncio
async def test_list_quizzes_admin_with_filters(mock_get_current_active_user, mock_get_quizzes):
    """Test quizzes listing with filters as admin"""
    # Arrange
    admin_user = MagicMock(spec=User)
    admin_user.id = TEST_USER_ADMIN["id"]
    admin_user.username = TEST_USER_ADMIN["username"]
    admin_user.role = TEST_USER_ADMIN["role"]
    admin_user.is_active = TEST_USER_ADMIN["is_active"]
    
    mock_get_current_active_user.return_value = admin_user
    
    # Create filtered QuizReadList objects (only draft)
    quiz_list = [QuizReadList.model_validate(TEST_QUIZ_LIST[1])]
    mock_get_quizzes.return_value = quiz_list
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/?sort_by=title&order=desc&status=draft")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "draft"
    
    # Verify service call with correct parameters
    mock_get_quizzes.assert_called_once()
    args, kwargs = mock_get_quizzes.call_args
    assert kwargs["sort_by"] == "title"
    assert kwargs["order"] == "desc"
    assert kwargs["status"] == "draft"

@pytest.mark.asyncio
async def test_list_quizzes_student_success(mock_get_current_active_user, mock_get_quizzes):
    """Test successful quizzes listing as student"""
    # Arrange
    student_user = MagicMock(spec=User)
    student_user.id = TEST_USER_STUDENT["id"]
    student_user.username = TEST_USER_STUDENT["username"]
    student_user.role = TEST_USER_STUDENT["role"]
    student_user.is_active = TEST_USER_STUDENT["is_active"]
    
    mock_get_current_active_user.return_value = student_user
    
    # Create QuizReadList objects for student (only published with last_result)
    quiz_list = [QuizReadList.model_validate(TEST_QUIZ_LIST_STUDENT[0])]
    mock_get_quizzes.return_value = quiz_list
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "published"
    assert response.json()[0]["last_result"] is not None
    assert response.json()[0]["last_result"]["score"] == 8
    assert response.json()[0]["last_result"]["max_score"] == 10

@pytest.mark.asyncio
async def test_list_quizzes_validation_error(mock_get_current_active_user, mock_get_quizzes):
    """Test quizzes listing with validation error"""
    # Arrange
    admin_user = MagicMock(spec=User)
    admin_user.id = TEST_USER_ADMIN["id"]
    admin_user.role = TEST_USER_ADMIN["role"]
    
    mock_get_current_active_user.return_value = admin_user
    mock_get_quizzes.side_effect = ValueError("Invalid sort_by parameter: invalid_field")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/?sort_by=invalid_field")
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid sort_by parameter" in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_quizzes_unexpected_error(mock_get_current_active_user, mock_get_quizzes):
    """Test quizzes listing with unexpected error"""
    # Arrange
    admin_user = MagicMock(spec=User)
    admin_user.id = TEST_USER_ADMIN["id"]
    admin_user.role = TEST_USER_ADMIN["role"]
    
    mock_get_current_active_user.return_value = admin_user
    mock_get_quizzes.side_effect = Exception("Unexpected error")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/")
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_quizzes_unauthorized():
    """Test quizzes listing with unauthorized user (no token)"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

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

# Test data for quiz detail endpoint
TEST_QUIZ_DETAIL = {
    "id": 1,
    "title": "Test Quiz",
    "status": "published",
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
        },
        {
            "id": 2,
            "text": "Question 2?",
            "answers": [
                {"id": 5, "text": "Answer 5", "is_correct": False},
                {"id": 6, "text": "Answer 6", "is_correct": True},
                {"id": 7, "text": "Answer 7", "is_correct": False},
                {"id": 8, "text": "Answer 8", "is_correct": False}
            ]
        }
    ]
}

@pytest.mark.asyncio
async def test_get_quiz_admin_success(mock_get_current_active_user, mock_get_quiz_by_id):
    """Test getting quiz details as admin"""
    # Arrange
    admin_user = MagicMock(spec=User)
    admin_user.id = TEST_USER_ADMIN["id"]
    admin_user.username = TEST_USER_ADMIN["username"]
    admin_user.role = TEST_USER_ADMIN["role"]
    admin_user.is_active = TEST_USER_ADMIN["is_active"]
    
    mock_get_current_active_user.return_value = admin_user
    
    # Create mock quiz object
    mock_quiz = MagicMock()
    for key, value in TEST_QUIZ_DETAIL.items():
        setattr(mock_quiz, key, value)
    
    mock_get_quiz_by_id.return_value = mock_quiz
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/1")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Quiz"
    assert len(data["questions"]) == 2
    
    # Verify admin gets is_correct field
    assert "is_correct" in data["questions"][0]["answers"][0]
    assert data["questions"][0]["answers"][0]["is_correct"] is True
    
    # Verify service call
    mock_get_quiz_by_id.assert_called_once_with(db=mock_get_quiz_by_id.call_args[1]["db"], quiz_id=1)

@pytest.mark.asyncio
async def test_get_quiz_student_success(mock_get_current_active_user, mock_get_quiz_by_id):
    """Test getting quiz details as student (without is_correct field)"""
    # Arrange
    student_user = MagicMock(spec=User)
    student_user.id = TEST_USER_STUDENT["id"]
    student_user.username = TEST_USER_STUDENT["username"]
    student_user.role = TEST_USER_STUDENT["role"]
    student_user.is_active = TEST_USER_STUDENT["is_active"]
    
    mock_get_current_active_user.return_value = student_user
    
    # Create mock quiz object
    mock_quiz = MagicMock()
    for key, value in TEST_QUIZ_DETAIL.items():
        setattr(mock_quiz, key, value)
    
    mock_get_quiz_by_id.return_value = mock_quiz
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/1")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Quiz"
    assert len(data["questions"]) == 2
    
    # Verify student does NOT get is_correct field
    assert "is_correct" not in data["questions"][0]["answers"][0]
    
    # Verify service call
    mock_get_quiz_by_id.assert_called_once_with(db=mock_get_quiz_by_id.call_args[1]["db"], quiz_id=1)

@pytest.mark.asyncio
async def test_get_quiz_not_found(mock_get_current_active_user, mock_get_quiz_by_id):
    """Test getting quiz that doesn't exist"""
    # Arrange
    admin_user = MagicMock(spec=User)
    admin_user.id = TEST_USER_ADMIN["id"]
    admin_user.username = TEST_USER_ADMIN["username"]
    admin_user.role = TEST_USER_ADMIN["role"]
    admin_user.is_active = TEST_USER_ADMIN["is_active"]
    
    mock_get_current_active_user.return_value = admin_user
    
    # Mock service to raise 404 exception
    from fastapi import HTTPException
    mock_get_quiz_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Quiz not found"
    )
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/999")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Quiz not found" in response.json()["detail"]
    
    # Verify service call
    mock_get_quiz_by_id.assert_called_once_with(db=mock_get_quiz_by_id.call_args[1]["db"], quiz_id=999)

@pytest.mark.asyncio
async def test_get_quiz_unauthorized():
    """Test getting quiz without authentication"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/1")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_quiz_server_error(mock_get_current_active_user, mock_get_quiz_by_id):
    """Test server error when getting quiz"""
    # Arrange
    admin_user = MagicMock(spec=User)
    admin_user.id = TEST_USER_ADMIN["id"]
    admin_user.username = TEST_USER_ADMIN["username"]
    admin_user.role = TEST_USER_ADMIN["role"]
    admin_user.is_active = TEST_USER_ADMIN["is_active"]
    
    mock_get_current_active_user.return_value = admin_user
    
    # Mock service to raise unexpected exception
    mock_get_quiz_by_id.side_effect = Exception("Database error")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/1")
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in response.json()["detail"] 