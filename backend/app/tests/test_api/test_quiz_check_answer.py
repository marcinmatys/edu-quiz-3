import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from fastapi import status, HTTPException

from ...main import app
from ...services.quiz_service import QuizService
from ...core.security import get_current_active_student
from ...schemas.question import AnswerCheckResponse

# Constants for testing
TEST_USER_STUDENT = {
    "id": 2,
    "username": "student",
    "role": "student",
    "is_active": True
}

TEST_USER_ADMIN = {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "is_active": True
}

TEST_ANSWER_CHECK_DATA = {
    "question_id": 1,
    "answer_id": 2
}

TEST_ANSWER_CHECK_RESPONSE = {
    "is_correct": True,
    "correct_answer_id": 2,
    "explanation": "This is the explanation for the correct answer."
}

@pytest.fixture
def authenticated_user(request):
    """
    Fixture to override the get_current_active_student dependency.
    Usage: @pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
    """
    user_data = request.param

    async def override_get_current_active_user():
        user = MagicMock()
        user.id = user_data["id"]
        user.username = user_data["username"]
        user.role = user_data["role"]
        user.is_active = user_data["is_active"]
        return user

    app.dependency_overrides[get_current_active_student] = override_get_current_active_user
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def mock_check_answer():
    """Mock the check_answer method of QuizService"""
    with patch.object(QuizService, "check_answer") as mock_check:
        # Setup the mock response
        response = AnswerCheckResponse(
            is_correct=TEST_ANSWER_CHECK_RESPONSE["is_correct"],
            correct_answer_id=TEST_ANSWER_CHECK_RESPONSE["correct_answer_id"],
            explanation=TEST_ANSWER_CHECK_RESPONSE["explanation"]
        )
        mock_check.return_value = response
        yield mock_check

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_check_answer_success(authenticated_user, mock_check_answer):
    """Test successful answer check"""
    # Arrange
    quiz_id = 1
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/quizzes/{quiz_id}/check-answer",
            json=TEST_ANSWER_CHECK_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_correct"] == TEST_ANSWER_CHECK_RESPONSE["is_correct"]
    assert response.json()["correct_answer_id"] == TEST_ANSWER_CHECK_RESPONSE["correct_answer_id"]
    assert response.json()["explanation"] == TEST_ANSWER_CHECK_RESPONSE["explanation"]
    
    # Verify service call
    mock_check_answer.assert_called_once()
    args, kwargs = mock_check_answer.call_args
    assert kwargs["quiz_id"] == quiz_id
    assert kwargs["answer_check_data"].question_id == TEST_ANSWER_CHECK_DATA["question_id"]
    assert kwargs["answer_check_data"].answer_id == TEST_ANSWER_CHECK_DATA["answer_id"]

@pytest.mark.asyncio
async def test_check_answer_unauthorized():
    """Test answer check with no authentication"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/quizzes/1/check-answer",
            json=TEST_ANSWER_CHECK_DATA
        )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_check_answer_quiz_not_found(authenticated_user):
    """Test answer check with non-existent quiz"""
    # Arrange
    with patch.object(QuizService, "check_answer") as mock_check:
        mock_check.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or not published"
        )
        
        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/quizzes/999/check-answer",
                json=TEST_ANSWER_CHECK_DATA
            )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Quiz not found" in response.json()["detail"]

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_check_answer_question_not_found(authenticated_user):
    """Test answer check with non-existent question"""
    # Arrange
    with patch.object(QuizService, "check_answer") as mock_check:
        mock_check.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found in this quiz"
        )
        
        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/quizzes/1/check-answer",
                json={"question_id": 999, "answer_id": 1}
            )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Question not found" in response.json()["detail"]

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_check_answer_answer_not_found(authenticated_user):
    """Test answer check with non-existent answer"""
    # Arrange
    with patch.object(QuizService, "check_answer") as mock_check:
        mock_check.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found for this question"
        )
        
        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/quizzes/1/check-answer",
                json={"question_id": 1, "answer_id": 999}
            )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Answer not found" in response.json()["detail"]

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_check_answer_server_error(authenticated_user):
    """Test answer check with server error"""
    # Arrange
    with patch.object(QuizService, "check_answer") as mock_check:
        mock_check.side_effect = Exception("Unexpected error")
        
        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/quizzes/1/check-answer",
                json=TEST_ANSWER_CHECK_DATA
            )
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "unexpected error" in response.json()["detail"].lower()

@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_user", [TEST_USER_STUDENT], indirect=True)
async def test_check_answer_validation_error(authenticated_user):
    """Test answer check with invalid input data"""
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/quizzes/1/check-answer",
            json={"question_id": "invalid", "answer_id": 1}  # question_id should be int
        )
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 