import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os

from ...services.ai_service import AIService

@pytest.fixture
def ai_service():
    """Create an instance of AIService with mocked API key and OpenAI clients, and return the service and mocks."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        with patch("app.services.ai_service.AsyncOpenAI") as mock_async_openai, \
             patch("app.services.ai_service.OpenAI") as mock_sync_openai:
            mock_async_client = MagicMock()
            mock_sync_client = MagicMock()
            mock_async_openai.return_value = mock_async_client
            mock_sync_openai.return_value = mock_sync_client
            service = AIService()
            yield service, mock_async_client, mock_sync_client

@pytest.mark.asyncio
async def test_generate_explanation_correct_answer(ai_service):
    service, mock_async_client, mock_sync_client = ai_service
    # Mock async response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="This is the correct explanation."))]
    mock_async_client.chat.completions.create = AsyncMock(return_value=mock_response)
    explanation = await service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4",
        is_student_correct=True
    )
    assert explanation == "This is the correct explanation."
    mock_async_client.chat.completions.create.assert_awaited_once()
    # Check prompt structure
    args, kwargs = mock_async_client.chat.completions.create.call_args
    assert "model" in kwargs
    assert "messages" in kwargs
    assert "The student answered correctly" in kwargs["messages"][1]["content"]
    assert "What is 2+2?" in kwargs["messages"][1]["content"]
    assert "4" in kwargs["messages"][1]["content"]

@pytest.mark.asyncio
async def test_generate_explanation_incorrect_answer(ai_service):
    service, mock_async_client, mock_sync_client = ai_service
    # Mock async response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="The correct answer is 4, not 5."))]
    mock_async_client.chat.completions.create = AsyncMock(return_value=mock_response)
    explanation = await service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4",
        student_answer_text="5",
        is_student_correct=False
    )
    assert explanation == "The correct answer is 4, not 5."
    mock_async_client.chat.completions.create.assert_awaited_once()
    # Check prompt structure
    args, kwargs = mock_async_client.chat.completions.create.call_args
    assert "model" in kwargs
    assert "messages" in kwargs
    assert "The student answered incorrectly" in kwargs["messages"][1]["content"]
    assert "What is 2+2?" in kwargs["messages"][1]["content"]
    assert "4" in kwargs["messages"][1]["content"]
    assert "5" in kwargs["messages"][1]["content"]

@pytest.mark.asyncio
async def test_generate_explanation_api_error(ai_service):
    service, mock_async_client, mock_sync_client = ai_service
    # Async call fails
    mock_async_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))
    # Sync call fails
    mock_sync_client.chat.completions.create = MagicMock(side_effect=Exception("API error"))
    explanation = await service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4"
    )
    assert "Explanation not available due to an unexpected error." in explanation

@pytest.mark.asyncio
async def test_generate_explanation_timeout(ai_service):
    service, mock_async_client, mock_sync_client = ai_service
    # Async call times out
    mock_async_client.chat.completions.create = AsyncMock(side_effect=Exception("Request timed out"))
    # Sync call times out
    mock_sync_client.chat.completions.create = MagicMock(side_effect=Exception("Request timed out"))
    explanation = await service.generate_explanation(
        quiz_title="Test Quiz",
        quiz_level="Beginner",
        question_text="What is 2+2?",
        correct_answer_text="4"
    )
    assert "Explanation not available due to an unexpected error." in explanation

@pytest.mark.asyncio
async def test_generate_explanation_no_api_key():
    """Test handling missing API key"""
    # Patch the settings object used by AIService to simulate no API key
    with patch("app.services.ai_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = None

        with patch("app.services.ai_service.AsyncOpenAI"), \
             patch("app.services.ai_service.OpenAI"):

            # AIService will now be initialized with api_key=None
            service = AIService()
            
            # Verify that the api_key is indeed None
            assert service.api_key is None

            explanation = await service.generate_explanation(
                quiz_title="Test Quiz",
                quiz_level="Beginner",
                question_text="What is 2+2?",
                correct_answer_text="4"
            )
            assert "Explanation not available. Please contact an administrator" in explanation
            
            # Verify that the mocked clients were not called
            service.client.chat.completions.create.assert_not_called()
            service.sync_client.chat.completions.create.assert_not_called() 