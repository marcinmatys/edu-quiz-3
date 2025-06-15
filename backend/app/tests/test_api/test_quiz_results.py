import pytest
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from httpx import AsyncClient
from fastapi import status, HTTPException
from typing import List, Dict, Any

from ...main import app
from ...services.quiz_service import QuizService
from ...models.user import User
from ...models.quiz import Quiz
from ...models.question import Question
from ...models.result import Result
from ...core.security import get_current_active_user
from ...crud import result as result_crud

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

# Test quiz with 5 questions
TEST_QUIZ = {
    "id": 1,
    "title": "Test Quiz",
    "status": "published",
    "level_id": 1,
    "creator_id": 1,
    "questions": [
        {"id": 1, "text": "Question 1?", "answers": []},
        {"id": 2, "text": "Question 2?", "answers": []},
        {"id": 3, "text": "Question 3?", "answers": []},
        {"id": 4, "text": "Question 4?", "answers": []},
        {"id": 5, "text": "Question 5?", "answers": []}
    ]
}

# Valid result data
VALID_RESULT_DATA = {
    "score": 4,
    "max_score": 5
}

# Invalid result data (score > max_score)
INVALID_SCORE_RESULT_DATA = {
    "score": 6,
    "max_score": 5
}

# Invalid result data (max_score != question_count)
INVALID_MAX_SCORE_RESULT_DATA = {
    "score": 3,
    "max_score": 10
}

@pytest.fixture
def authenticated_user(request):
    """
    Fixture to override the get_current_active_user dependency.
    Usage: @pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
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
def mock_get_quiz_by_id():
    """Mock the get_quiz_by_id method of QuizService"""
    with patch.object(QuizService, "get_quiz_by_id") as mock_get:
        yield mock_get

@pytest.fixture
def mock_get_by_user_and_quiz():
    """Mock the get_by_user_and_quiz method from result_crud"""
    with patch.object(result_crud, "get_by_user_and_quiz") as mock_get:
        yield mock_get

@pytest.fixture
def mock_create_with_owner():
    """Mock the create_with_owner method from result_crud"""
    with patch.object(result_crud, "create_with_owner") as mock_create:
        yield mock_create

@pytest.fixture
def mock_update():
    """Mock the update method from result_crud"""
    with patch.object(result_crud, "update") as mock_update:
        yield mock_update

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_submit_quiz_result_create_success(
    authenticated_user, 
    mock_get_quiz_by_id, 
    mock_get_by_user_and_quiz,
    mock_create_with_owner
):
    """Test successful quiz result submission (create new result)"""
    # Arrange
    quiz_id = 1
    
    # Mock quiz retrieval
    quiz = MagicMock(spec=Quiz)
    quiz.id = TEST_QUIZ["id"]
    quiz.title = TEST_QUIZ["title"]
    quiz.questions = []
    # Add 5 question objects to the quiz
    for q_data in TEST_QUIZ["questions"]:
        question = MagicMock(spec=Question)
        question.id = q_data["id"]
        question.text = q_data["text"]
        quiz.questions.append(question)
    
    mock_get_quiz_by_id.return_value = quiz
    
    # Mock result retrieval (not found)
    mock_get_by_user_and_quiz.return_value = None
    
    # Mock result creation
    created_result = MagicMock(spec=Result)
    created_result.id = 1
    created_result.score = VALID_RESULT_DATA["score"]
    created_result.max_score = VALID_RESULT_DATA["max_score"]
    created_result.user_id = TEST_USER_STUDENT["id"]
    created_result.quiz_id = quiz_id
    created_result.created_at = "2023-10-27T14:00:00Z"
    
    mock_create_with_owner.return_value = created_result
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/quizzes/{quiz_id}/results",
            json=VALID_RESULT_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["score"] == VALID_RESULT_DATA["score"]
    assert response.json()["max_score"] == VALID_RESULT_DATA["max_score"]
    assert response.json()["user_id"] == TEST_USER_STUDENT["id"]
    assert response.json()["quiz_id"] == quiz_id
    
    # Verify service calls
    mock_get_quiz_by_id.assert_called_once_with(db=ANY, quiz_id=quiz_id)
    mock_get_by_user_and_quiz.assert_called_once_with(
        db=ANY, 
        user_id=TEST_USER_STUDENT["id"], 
        quiz_id=quiz_id
    )
    mock_create_with_owner.assert_called_once_with(
        db=ANY,
        obj_in=ANY,
        user_id=TEST_USER_STUDENT["id"],
        quiz_id=quiz_id
    )

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_submit_quiz_result_update_success(
    authenticated_user, 
    mock_get_quiz_by_id, 
    mock_get_by_user_and_quiz,
    mock_update
):
    """Test successful quiz result submission (update existing result)"""
    # Arrange
    quiz_id = 1
    
    # Mock quiz retrieval
    quiz = MagicMock(spec=Quiz)
    quiz.id = TEST_QUIZ["id"]
    quiz.title = TEST_QUIZ["title"]
    quiz.questions = []
    # Add 5 question objects to the quiz
    for q_data in TEST_QUIZ["questions"]:
        question = MagicMock(spec=Question)
        question.id = q_data["id"]
        question.text = q_data["text"]
        quiz.questions.append(question)
    
    mock_get_quiz_by_id.return_value = quiz
    
    # Mock result retrieval (existing result)
    existing_result = MagicMock(spec=Result)
    existing_result.id = 1
    existing_result.score = 3  # Old score
    existing_result.max_score = 5
    existing_result.user_id = TEST_USER_STUDENT["id"]
    existing_result.quiz_id = quiz_id
    
    mock_get_by_user_and_quiz.return_value = existing_result
    
    # Mock result update
    updated_result = MagicMock(spec=Result)
    updated_result.id = 1
    updated_result.score = VALID_RESULT_DATA["score"]  # New score
    updated_result.max_score = VALID_RESULT_DATA["max_score"]
    updated_result.user_id = TEST_USER_STUDENT["id"]
    updated_result.quiz_id = quiz_id
    updated_result.created_at = "2023-10-27T14:00:00Z"
    
    mock_update.return_value = updated_result
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/quizzes/{quiz_id}/results",
            json=VALID_RESULT_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["score"] == VALID_RESULT_DATA["score"]
    assert response.json()["max_score"] == VALID_RESULT_DATA["max_score"]
    assert response.json()["user_id"] == TEST_USER_STUDENT["id"]
    assert response.json()["quiz_id"] == quiz_id
    
    # Verify service calls
    mock_get_quiz_by_id.assert_called_once_with(db=ANY, quiz_id=quiz_id)
    mock_get_by_user_and_quiz.assert_called_once_with(
        db=ANY, 
        user_id=TEST_USER_STUDENT["id"], 
        quiz_id=quiz_id
    )
    mock_update.assert_called_once_with(
        db=ANY,
        db_obj=existing_result,
        obj_in=ANY
    )

@pytest.mark.asyncio
async def test_submit_quiz_result_unauthorized():
    """Test quiz result submission without authentication"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/quizzes/1/results",
            json=VALID_RESULT_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_ADMIN], indirect=True)
async def test_submit_quiz_result_forbidden(authenticated_user):
    """Test quiz result submission with admin role (should be forbidden)"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/quizzes/1/results",
            json=VALID_RESULT_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_submit_quiz_result_quiz_not_found(authenticated_user, mock_get_quiz_by_id):
    """Test quiz result submission for non-existent quiz"""
    # Arrange
    quiz_id = 999  # Non-existent quiz ID
    
    # Mock quiz retrieval (not found)
    mock_get_quiz_by_id.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Quiz with id {quiz_id} not found"
    )
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/quizzes/{quiz_id}/results",
            json=VALID_RESULT_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_submit_quiz_result_invalid_score(authenticated_user, mock_get_quiz_by_id):
    """Test quiz result submission with invalid score (score > max_score)"""
    # Arrange
    quiz_id = 1
    
    # Mock quiz retrieval
    quiz = MagicMock(spec=Quiz)
    quiz.id = TEST_QUIZ["id"]
    quiz.title = TEST_QUIZ["title"]
    quiz.questions = []
    # Add 5 question objects to the quiz
    for q_data in TEST_QUIZ["questions"]:
        question = MagicMock(spec=Question)
        question.id = q_data["id"]
        question.text = q_data["text"]
        quiz.questions.append(question)
    
    mock_get_quiz_by_id.return_value = quiz
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/quizzes/{quiz_id}/results",
            json=INVALID_SCORE_RESULT_DATA  # score > max_score
        )
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "score cannot be greater than max_score" in response.json()["detail"].lower()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_submit_quiz_result_invalid_max_score(authenticated_user, mock_get_quiz_by_id):
    """Test quiz result submission with invalid max_score (max_score != question_count)"""
    # Arrange
    quiz_id = 1
    
    # Mock quiz retrieval
    quiz = MagicMock(spec=Quiz)
    quiz.id = TEST_QUIZ["id"]
    quiz.title = TEST_QUIZ["title"]
    quiz.questions = []
    # Add 5 question objects to the quiz
    for q_data in TEST_QUIZ["questions"]:
        question = MagicMock(spec=Question)
        question.id = q_data["id"]
        question.text = q_data["text"]
        quiz.questions.append(question)
    
    mock_get_quiz_by_id.return_value = quiz
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/quizzes/{quiz_id}/results",
            json=INVALID_MAX_SCORE_RESULT_DATA  # max_score != question_count
        )
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "max_score must match the number of questions" in response.json()["detail"].lower()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_submit_quiz_result_server_error(
    authenticated_user, 
    mock_get_quiz_by_id, 
    mock_get_by_user_and_quiz
):
    """Test quiz result submission with server error"""
    # Arrange
    quiz_id = 1
    
    # Mock quiz retrieval
    quiz = MagicMock(spec=Quiz)
    quiz.id = TEST_QUIZ["id"]
    quiz.title = TEST_QUIZ["title"]
    quiz.questions = []
    # Add 5 question objects to the quiz
    for q_data in TEST_QUIZ["questions"]:
        question = MagicMock(spec=Question)
        question.id = q_data["id"]
        question.text = q_data["text"]
        quiz.questions.append(question)
    
    mock_get_quiz_by_id.return_value = quiz
    
    # Mock result retrieval (throws exception)
    mock_get_by_user_and_quiz.side_effect = Exception("Database connection error")
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/quizzes/{quiz_id}/results",
            json=VALID_RESULT_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "unexpected error" in response.json()["detail"].lower() 