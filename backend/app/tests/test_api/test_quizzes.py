import pytest
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from httpx import AsyncClient
from fastapi import status, HTTPException
from typing import List

from ...main import app
from ...services.quiz_service import QuizService
from ...services.ai_quiz_generator import AIGenerationError
from ...models.user import User
from ...schemas.quiz import QuizReadList, LastResult
from ...core.security import get_current_active_user

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
def authenticated_user(request):
    """
    Fixture to override the get_current_active_user dependency.
    Usage: @pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
    """
    user_data = request.param

    async def override_get_current_active_user():
        user = MagicMock(spec=User)
        user.id = user_data["id"]
        user.username = user_data["username"]
        user.role = user_data["role"]
        user.is_active = user_data["is_active"]
        return user

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    yield
    app.dependency_overrides.clear()

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

@pytest.fixture
def mock_update_quiz():
    """Mock the quiz_service.update_quiz method"""
    with patch("app.routers.quizzes.quiz_service.update_quiz") as mock:
        yield mock

@pytest.fixture
def mock_remove_quiz():
    """Mock the remove_quiz function from crud module"""
    with patch("app.routers.quizzes.remove_quiz") as mock:
        yield mock

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_list_quizzes_admin_success(authenticated_user, mock_get_quizzes):
    """Test successful quizzes listing as admin"""
    # Arrange
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_list_quizzes_admin_with_filters(authenticated_user, mock_get_quizzes):
    """Test quizzes listing with filters as admin"""
    # Arrange
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_list_quizzes_student_success(authenticated_user, mock_get_quizzes):
    """Test successful quizzes listing as student"""
    # Arrange
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

# @pytest.mark.asyncio
# @pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
# async def test_list_quizzes_validation_error(authenticated_user, mock_get_quizzes):
#     """Test quizzes listing with validation error"""
#     # Arrange
#     mock_get_quizzes.side_effect = ValueError("Invalid sort_by parameter: invalid_field")
    
#     # Act
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.get("/api/v1/quizzes/?sort_by=invalid_field")
    
#     # Assert
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Invalid sort_by parameter" in response.json()["detail"]

# @pytest.mark.asyncio
# @pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
# async def test_list_quizzes_unexpected_error(authenticated_user, mock_get_quizzes):
#     """Test quizzes listing with unexpected error"""
#     # Arrange
#     mock_get_quizzes.side_effect = Exception("Unexpected error")
    
#     # Act
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.get("/api/v1/quizzes/")
    
#     # Assert
#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#     assert "An unexpected error occurred" in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_quizzes_unauthorized():
    """Test quizzes listing with unauthorized user (no token)"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_create_quiz_success(authenticated_user, mock_quiz_service):
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_create_quiz_validation_error(authenticated_user, mock_quiz_service):
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_create_quiz_ai_error(authenticated_user, mock_quiz_service):
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_create_quiz_unexpected_error(authenticated_user, mock_quiz_service):
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_create_quiz_invalid_input(authenticated_user):
    """Test quiz creation with invalid input data"""
    # Invalid data (missing required fields)
    invalid_data = {
        "topic": "Test Topic",
        # Missing question_count
        "level_id": 1
    }
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_get_quiz_admin_success(authenticated_user, mock_get_quiz_by_id):
    """Test getting quiz details as admin"""
    # Arrange
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_get_quiz_student_success(authenticated_user, mock_get_quiz_by_id):
    """Test getting quiz details as student (without is_correct field)"""
    # Arrange
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_get_quiz_not_found(authenticated_user, mock_get_quiz_by_id):
    """Test getting quiz that doesn't exist"""
    # Arrange
    # Mock service to raise 404 exception
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
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_get_quiz_server_error(authenticated_user, mock_get_quiz_by_id):
    """Test server error when getting quiz"""
    # Arrange
    # Mock service to raise unexpected exception
    mock_get_quiz_by_id.side_effect = Exception("Database error")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/quizzes/1")
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in response.json()["detail"]

# Test data for quiz update
TEST_QUIZ_UPDATE_DATA = {
    "title": "Updated Quiz Title",
    "level_id": 1,
    "status": "published",
    "questions": [
        {
            "id": 1,
            "text": "Updated Question 1?",
            "answers": [
                {"id": 1, "text": "Updated Answer 1", "is_correct": True},
                {"id": 2, "text": "Updated Answer 2", "is_correct": False},
                {"text": "New Answer", "is_correct": False}
            ]
        },
        {
            "text": "New Question?",
            "answers": [
                {"text": "New Question Answer 1", "is_correct": True},
                {"text": "New Question Answer 2", "is_correct": False}
            ]
        }
    ]
}

# Updated quiz response
TEST_UPDATED_QUIZ = {
    "id": 1,
    "title": "Updated Quiz Title",
    "status": "published",
    "level_id": 1,
    "creator_id": 1,
    "updated_at": "2023-06-15T12:00:00",
    "questions": [
        {
            "id": 1,
            "text": "Updated Question 1?",
            "answers": [
                {"id": 1, "text": "Updated Answer 1", "is_correct": True},
                {"id": 2, "text": "Updated Answer 2", "is_correct": False},
                {"id": 3, "text": "New Answer", "is_correct": False}
            ]
        },
        {
            "id": 2,
            "text": "New Question?",
            "answers": [
                {"id": 4, "text": "New Question Answer 1", "is_correct": True},
                {"id": 5, "text": "New Question Answer 2", "is_correct": False}
            ]
        }
    ]
}

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_update_quiz_success(authenticated_user, mock_update_quiz):
    """Test successful quiz update"""
    # Arrange
    mock_update_quiz.return_value = MagicMock(**TEST_UPDATED_QUIZ)
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/api/v1/quizzes/1", json=TEST_QUIZ_UPDATE_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == TEST_QUIZ_UPDATE_DATA["title"]
    assert data["status"] == TEST_QUIZ_UPDATE_DATA["status"]
    assert len(data["questions"]) == len(TEST_QUIZ_UPDATE_DATA["questions"])
    
    # Verify first question was updated
    assert data["questions"][0]["text"] == TEST_QUIZ_UPDATE_DATA["questions"][0]["text"]
    assert len(data["questions"][0]["answers"]) == 3  # Two existing answers + one new
    
    # Verify second question was added
    assert data["questions"][1]["text"] == TEST_QUIZ_UPDATE_DATA["questions"][1]["text"]
    assert len(data["questions"][1]["answers"]) == 2
    
    # Verify service call
    mock_update_quiz.assert_called_once()
    args, kwargs = mock_update_quiz.call_args
    assert kwargs["quiz_id"] == 1
    assert kwargs["quiz_data"].title == TEST_QUIZ_UPDATE_DATA["title"]
    assert kwargs["quiz_data"].status == TEST_QUIZ_UPDATE_DATA["status"]
    assert len(kwargs["quiz_data"].questions) == len(TEST_QUIZ_UPDATE_DATA["questions"])

@pytest.mark.asyncio
async def test_update_quiz_unauthorized(mock_update_quiz):
    """Test quiz update without authentication"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/api/v1/quizzes/1", json=TEST_QUIZ_UPDATE_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Verify service was not called
    mock_update_quiz.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_update_quiz_forbidden(authenticated_user, mock_update_quiz):
    """Test quiz update as student (forbidden)"""
    # Arrange
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/api/v1/quizzes/1", json=TEST_QUIZ_UPDATE_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Verify service was not called
    mock_update_quiz.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_update_quiz_not_found(authenticated_user, mock_update_quiz):
    """Test quiz update when quiz not found"""
    # Arrange
    mock_update_quiz.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Quiz with ID 999 not found"
    )
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/api/v1/quizzes/999", json=TEST_QUIZ_UPDATE_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
    
    # Verify service call
    mock_update_quiz.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_update_quiz_validation_error(authenticated_user, mock_update_quiz):
    """Test quiz update with validation error"""
    # Arrange
    mock_update_quiz.side_effect = ValueError("Invalid quiz data")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/api/v1/quizzes/1", json=TEST_QUIZ_UPDATE_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Invalid quiz data" in response.json()["detail"]
    
    # Verify service call
    mock_update_quiz.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_update_quiz_server_error(authenticated_user, mock_update_quiz):
    """Test quiz update with server error"""
    # Arrange
    mock_update_quiz.side_effect = Exception("Unexpected error")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put("/api/v1/quizzes/1", json=TEST_QUIZ_UPDATE_DATA)
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "unexpected error" in response.json()["detail"].lower()
    
    # Verify service call
    mock_update_quiz.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_delete_quiz_success(authenticated_user, mock_get_quiz_by_id, mock_remove_quiz):
    """Test successful quiz deletion as admin"""
    # Arrange
    quiz_id = 1
    mock_get_quiz_by_id.return_value = TEST_GENERATED_QUIZ
    mock_remove_quiz.return_value = TEST_GENERATED_QUIZ
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/quizzes/{quiz_id}")
    
    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''  # No content in response body
    
    # Verify service calls
    mock_get_quiz_by_id.assert_called_once_with(db=ANY, quiz_id=quiz_id)
    mock_remove_quiz.assert_called_once_with(db=ANY, quiz_id=quiz_id)

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_delete_quiz_not_found(authenticated_user, mock_get_quiz_by_id):
    """Test quiz deletion when quiz not found"""
    # Arrange
    quiz_id = 999
    mock_get_quiz_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Quiz not found"
    )
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/quizzes/{quiz_id}")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Quiz not found"
    
    # Verify service call
    mock_get_quiz_by_id.assert_called_once_with(db=ANY, quiz_id=quiz_id)

@pytest.mark.asyncio
async def test_delete_quiz_unauthorized():
    """Test quiz deletion without authentication"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/api/v1/quizzes/1")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_delete_quiz_forbidden(authenticated_user):
    """Test quiz deletion as student (should be forbidden)"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/api/v1/quizzes/1")
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Not enough permissions" in response.json()["detail"]

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_delete_quiz_server_error(authenticated_user, mock_get_quiz_by_id, mock_remove_quiz):
    """Test quiz deletion with server error"""
    # Arrange
    quiz_id = 1
    mock_get_quiz_by_id.return_value = TEST_GENERATED_QUIZ
    mock_remove_quiz.side_effect = Exception("Database error")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/quizzes/{quiz_id}")
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred" in response.json()["detail"] 