import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from ...services.ai_quiz_generator import AIQuizGeneratorService, AIGenerationError

# Test data
MOCK_LEVEL = {
    "id": 1,
    "code": "intermediate",
    "description": "Intermediate level",
    "level": 2
}

MOCK_AI_RESPONSE = json.dumps({
    "title": "Test Quiz",
    "questions": [
        {
            "text": "Question 1?",
            "answers": [
                {"text": "Answer 1", "is_correct": True},
                {"text": "Answer 2", "is_correct": False},
                {"text": "Answer 3", "is_correct": False},
                {"text": "Answer 4", "is_correct": False}
            ]
        },
        {
            "text": "Question 2?",
            "answers": [
                {"text": "Answer 1", "is_correct": False},
                {"text": "Answer 2", "is_correct": True},
                {"text": "Answer 3", "is_correct": False},
                {"text": "Answer 4", "is_correct": False}
            ]
        }
    ]
})

MOCK_AI_RESPONSE_WITH_CODE_BLOCK = f"```json\n{MOCK_AI_RESPONSE}\n```"

@pytest.fixture
def mock_openai():
    """Mock the OpenAI API responses"""
    with patch("openai.ChatCompletion.acreate") as mock_create:
        # Create a mock response object
        mock_response = AsyncMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_AI_RESPONSE
        
        # Set the mock to return the response
        mock_create.return_value = mock_response
        yield mock_create

# @pytest.mark.asyncio
# async def test_generate_quiz_success(mock_openai):
#     """Test successful quiz generation"""
#     # Arrange
#     service = AIQuizGeneratorService(openai_api_key="test_key")
#     topic = "Test Topic"
#     question_count = 2
    
#     # Act
#     questions, title = await service.generate_quiz(topic, question_count, MOCK_LEVEL)
    
#     # Assert
#     assert mock_openai.called
#     assert title == "Test Quiz"
#     assert len(questions) == 2
#     assert questions[0]["text"] == "Question 1?"
#     assert questions[1]["text"] == "Question 2?"
#     assert len(questions[0]["answers"]) == 4
#     assert questions[0]["answers"][0]["is_correct"] is True

@pytest.mark.asyncio
async def test_parse_response_with_code_block():
    """Test parsing response with code block"""
    # Arrange
    service = AIQuizGeneratorService(openai_api_key="test_key")
    
    # Act
    questions, title = service._parse_response(MOCK_AI_RESPONSE_WITH_CODE_BLOCK)
    
    # Assert
    assert title == "Test Quiz"
    assert len(questions) == 2

@pytest.mark.asyncio
async def test_parse_response_invalid_json():
    """Test parsing invalid JSON response"""
    # Arrange
    service = AIQuizGeneratorService(openai_api_key="test_key")
    invalid_response = "This is not valid JSON"
    
    # Act / Assert
    with pytest.raises(AIGenerationError) as exc_info:
        service._parse_response(invalid_response)
    
    assert "Invalid JSON" in str(exc_info.value)

@pytest.mark.asyncio
async def test_parse_response_missing_fields():
    """Test parsing response with missing required fields"""
    # Arrange
    service = AIQuizGeneratorService(openai_api_key="test_key")
    incomplete_response = json.dumps({
        "title": "Test Quiz",
        # Missing questions field
    })
    
    # Act / Assert
    with pytest.raises(AIGenerationError) as exc_info:
        service._parse_response(incomplete_response)
    
    assert "Invalid quiz structure" in str(exc_info.value)

@pytest.mark.asyncio
async def test_parse_response_invalid_question_structure():
    """Test parsing response with invalid question structure"""
    # Arrange
    service = AIQuizGeneratorService(openai_api_key="test_key")
    invalid_question = json.dumps({
        "title": "Test Quiz",
        "questions": [
            {
                "text": "Question 1?",
                # Missing answers field
            }
        ]
    })
    
    # Act / Assert
    with pytest.raises(AIGenerationError) as exc_info:
        service._parse_response(invalid_question)
    
    assert "Invalid quiz structure" in str(exc_info.value)

@pytest.mark.asyncio
async def test_parse_response_invalid_correct_answer_count():
    """Test parsing response with invalid correct answer count"""
    # Arrange
    service = AIQuizGeneratorService(openai_api_key="test_key")
    invalid_answers = json.dumps({
        "title": "Test Quiz",
        "questions": [
            {
                "text": "Question 1?",
                "answers": [
                    {"text": "Answer 1", "is_correct": True},
                    {"text": "Answer 2", "is_correct": True},  # Two correct answers
                    {"text": "Answer 3", "is_correct": False},
                    {"text": "Answer 4", "is_correct": False}
                ]
            }
        ]
    })
    
    # Act / Assert
    with pytest.raises(AIGenerationError) as exc_info:
        service._parse_response(invalid_answers)
    
    assert "Invalid quiz structure" in str(exc_info.value)

@pytest.mark.asyncio
async def test_api_error_handling(mock_openai):
    """Test handling of API errors"""
    # Arrange
    service = AIQuizGeneratorService(openai_api_key="test_key")
    mock_openai.side_effect = Exception("API Error")
    
    # Act / Assert
    with pytest.raises(AIGenerationError) as exc_info:
        await service.generate_quiz("Topic", 2, MOCK_LEVEL)
    
    assert "Failed to generate quiz" in str(exc_info.value) 