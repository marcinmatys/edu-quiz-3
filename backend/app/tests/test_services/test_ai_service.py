import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import os

from ...services.ai_service import AIService

@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient"""
    with patch("httpx.AsyncClient") as mock_client:
        # Setup the mock client
        mock_instance = MagicMock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_instance.post = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def ai_service():
    """Create an instance of AIService with mocked API key"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        service = AIService()
        yield service

@pytest.mark.asyncio
async def test_generate_explanation_correct_answer(ai_service, mock_httpx_client):
    """Test generating explanation for correct answer"""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is the correct explanation."}}]
    }
    mock_httpx_client.post.return_value = mock_response
    
    # Act
    explanation = await ai_service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4",
        is_student_correct=True
    )
    
    # Assert
    assert explanation == "This is the correct explanation."
    mock_httpx_client.post.assert_called_once()
    
    # Verify prompt structure for correct answer
    args, kwargs = mock_httpx_client.post.call_args
    assert "model" in kwargs["json"]
    assert "messages" in kwargs["json"]
    assert "The student answered correctly" in kwargs["json"]["messages"][0]["content"]
    assert "What is 2+2?" in kwargs["json"]["messages"][0]["content"]
    assert "4" in kwargs["json"]["messages"][0]["content"]

@pytest.mark.asyncio
async def test_generate_explanation_incorrect_answer(ai_service, mock_httpx_client):
    """Test generating explanation for incorrect answer"""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "The correct answer is 4, not 5."}}]
    }
    mock_httpx_client.post.return_value = mock_response
    
    # Act
    explanation = await ai_service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4",
        student_answer_text="5",
        is_student_correct=False
    )
    
    # Assert
    assert explanation == "The correct answer is 4, not 5."
    mock_httpx_client.post.assert_called_once()
    
    # Verify prompt structure for incorrect answer
    args, kwargs = mock_httpx_client.post.call_args
    assert "model" in kwargs["json"]
    assert "messages" in kwargs["json"]
    assert "The student answered incorrectly" in kwargs["json"]["messages"][0]["content"]
    assert "What is 2+2?" in kwargs["json"]["messages"][0]["content"]
    assert "4" in kwargs["json"]["messages"][0]["content"]
    assert "5" in kwargs["json"]["messages"][0]["content"]

@pytest.mark.asyncio
async def test_generate_explanation_api_error(ai_service, mock_httpx_client):
    """Test handling API error"""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal server error"}
    mock_httpx_client.post.return_value = mock_response
    
    # Act
    explanation = await ai_service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4"
    )
    
    # Assert
    assert "Explanation not available due to a service error" in explanation

@pytest.mark.asyncio
async def test_generate_explanation_timeout(ai_service, mock_httpx_client):
    """Test handling timeout exception"""
    # Arrange
    mock_httpx_client.post.side_effect = httpx.TimeoutException("Request timed out")
    
    # Act
    explanation = await ai_service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4"
    )
    
    # Assert
    assert "Explanation not available due to service timeout" in explanation

@pytest.mark.asyncio
async def test_generate_explanation_no_api_key(mock_httpx_client):
    """Test handling missing API key"""
    # Arrange - create service with no API key
    with patch.dict(os.environ, {}, clear=True):
        service = AIService()
    
    # Act
    explanation = await service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4"
    )
    
    # Assert
    assert "Explanation not available. Please contact an administrator" in explanation
    # Verify no API call was made
    mock_httpx_client.post.assert_not_called() 