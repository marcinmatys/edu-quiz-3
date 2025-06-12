import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ...services.quiz_service import QuizService
from ...services.ai_quiz_generator import AIGenerationError
from ...schemas.quiz import QuizCreate
from ...schemas.question import QuestionCreate
from ...schemas.answer import AnswerCreate

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock(spec=AsyncSession)
    db.begin = AsyncMock(return_value=AsyncMock(__aenter__=AsyncMock(), __aexit__=AsyncMock()))
    return db

@pytest.fixture
def mock_ai_generator():
    """Mock AI generator service"""
    with patch("app.services.quiz_service.AIQuizGeneratorService") as mock_service:
        # Setup the mock
        instance = mock_service.return_value
        instance.generate_quiz = AsyncMock()
        yield instance

@pytest.fixture
def mock_crud():
    """Mock CRUD operations"""
    with patch("app.services.quiz_service.get_level") as mock_get_level, \
         patch("app.services.quiz_service.create_quiz") as mock_create_quiz, \
         patch("app.services.quiz_service.create_question") as mock_create_question, \
         patch("app.services.quiz_service.get_quiz") as mock_get_quiz:
        
        # Setup mock level
        mock_level = MagicMock()
        mock_level.id = 1
        mock_level.code = "intermediate"
        mock_level.description = "Intermediate level"
        mock_level.level = 2
        mock_get_level.return_value = mock_level
        
        # Setup mock quiz
        mock_quiz = MagicMock()
        mock_quiz.id = 1
        mock_quiz.title = "Test Quiz"
        mock_quiz.status = "draft"
        mock_quiz.level_id = 1
        mock_quiz.creator_id = 1
        mock_create_quiz.return_value = mock_quiz
        
        # Setup mock question
        mock_question = MagicMock()
        mock_question.id = 1
        mock_question.text = "Test Question"
        mock_question.quiz_id = 1
        mock_create_question.return_value = mock_question
        
        # Setup mock quiz with relations
        mock_quiz_with_relations = MagicMock()
        mock_quiz_with_relations.id = 1
        mock_quiz_with_relations.title = "Test Quiz"
        mock_quiz_with_relations.status = "draft"
        mock_quiz_with_relations.level_id = 1
        mock_quiz_with_relations.creator_id = 1
        mock_quiz_with_relations.questions = [mock_question]
        mock_get_quiz.return_value = mock_quiz_with_relations
        
        yield {
            "get_level": mock_get_level,
            "create_quiz": mock_create_quiz,
            "create_question": mock_create_question,
            "get_quiz": mock_get_quiz,
            "mock_level": mock_level,
            "mock_quiz": mock_quiz,
            "mock_question": mock_question,
            "mock_quiz_with_relations": mock_quiz_with_relations
        }

@pytest.mark.asyncio
async def test_create_ai_quiz_success(mock_db, mock_ai_generator, mock_crud):
    """Test successful quiz creation"""
    # Arrange
    service = QuizService()
    quiz_data = QuizCreate(
        topic="Test Topic",
        question_count=2,
        level_id=1,
        title="Test Quiz"  # This will be ignored as AI will generate title
    )
    creator_id = 1
    
    # Setup AI generator mock response
    questions_data = [
        {
            "text": "Question 1?",
            "answers": [
                {"text": "Answer 1", "is_correct": True},
                {"text": "Answer 2", "is_correct": False},
                {"text": "Answer 3", "is_correct": False},
                {"text": "Answer 4", "is_correct": False}
            ]
        }
    ]
    title = "Generated Quiz Title"
    mock_ai_generator.generate_quiz.return_value = (questions_data, title)
    
    # Act
    result = await service.create_ai_quiz(mock_db, quiz_data, creator_id)
    
    # Assert
    assert mock_crud["get_level"].called
    assert mock_crud["create_quiz"].called
    assert mock_crud["create_question"].called
    assert mock_crud["get_quiz"].called
    
    # Check parameters passed to create_quiz
    mock_crud["create_quiz"].assert_called_once()
    call_args = mock_crud["create_quiz"].call_args[1]
    assert call_args["title"] == title
    assert call_args["level_id"] == quiz_data.level_id
    assert call_args["creator_id"] == creator_id
    assert call_args["status"] == "draft"

@pytest.mark.asyncio
async def test_create_ai_quiz_level_not_found(mock_db, mock_crud):
    """Test level not found error"""
    # Arrange
    service = QuizService()
    quiz_data = QuizCreate(
        topic="Test Topic",
        question_count=2,
        level_id=999,  # Non-existent level
        title="Test Quiz"
    )
    creator_id = 1
    
    # Setup mock to return None for level
    mock_crud["get_level"].return_value = None
    
    # Act / Assert
    with pytest.raises(ValueError) as exc_info:
        await service.create_ai_quiz(mock_db, quiz_data, creator_id)
    
    assert "Level with ID 999 not found" in str(exc_info.value)
    assert not mock_crud["create_quiz"].called

@pytest.mark.asyncio
async def test_create_ai_quiz_ai_generation_error(mock_db, mock_ai_generator, mock_crud):
    """Test AI generation error handling"""
    # Arrange
    service = QuizService()
    quiz_data = QuizCreate(
        topic="Test Topic",
        question_count=2,
        level_id=1,
        title="Test Quiz"
    )
    creator_id = 1
    
    # Setup AI generator to raise error
    mock_ai_generator.generate_quiz.side_effect = AIGenerationError("AI Error")
    
    # Act / Assert
    with pytest.raises(AIGenerationError) as exc_info:
        await service.create_ai_quiz(mock_db, quiz_data, creator_id)
    
    assert "AI Error" in str(exc_info.value)
    assert not mock_crud["create_quiz"].called

@pytest.mark.asyncio
async def test_create_ai_quiz_database_error(mock_db, mock_ai_generator, mock_crud):
    """Test database error handling"""
    # Arrange
    service = QuizService()
    quiz_data = QuizCreate(
        topic="Test Topic",
        question_count=2,
        level_id=1,
        title="Test Quiz"
    )
    creator_id = 1
    
    # Setup AI generator mock response
    questions_data = [
        {
            "text": "Question 1?",
            "answers": [
                {"text": "Answer 1", "is_correct": True},
                {"text": "Answer 2", "is_correct": False},
                {"text": "Answer 3", "is_correct": False},
                {"text": "Answer 4", "is_correct": False}
            ]
        }
    ]
    title = "Generated Quiz Title"
    mock_ai_generator.generate_quiz.return_value = (questions_data, title)
    
    # Setup database to raise error
    mock_crud["create_quiz"].side_effect = SQLAlchemyError("Database Error")
    
    # Act / Assert
    with pytest.raises(SQLAlchemyError) as exc_info:
        await service.create_ai_quiz(mock_db, quiz_data, creator_id)
    
    assert "Database Error" in str(exc_info.value) 