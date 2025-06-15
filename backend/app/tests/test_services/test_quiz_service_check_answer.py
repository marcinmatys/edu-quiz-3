import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ...services.quiz_service import QuizService
from ...services.ai_service import AIService
from ...schemas.answer import AnswerCheck
from ...models.user import User
from ...models.quiz import Quiz
from ...models.question import Question
from ...models.answer import Answer
from ...models.level import Level

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock(spec=AsyncSession)
    return db

@pytest.fixture
def mock_student_user():
    """Mock student user"""
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "student"
    user.role = "student"
    user.is_active = True
    return user

@pytest.fixture
def mock_admin_user():
    """Mock admin user"""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "admin"
    user.role = "admin"
    user.is_active = True
    return user

@pytest.fixture
def mock_quiz_with_questions():
    """Mock quiz with questions and answers"""
    # Create mock answers
    correct_answer = MagicMock(spec=Answer)
    correct_answer.id = 1
    correct_answer.text = "Correct answer"
    correct_answer.is_correct = True
    
    incorrect_answer = MagicMock(spec=Answer)
    incorrect_answer.id = 2
    incorrect_answer.text = "Incorrect answer"
    incorrect_answer.is_correct = False
    
    # Create mock question
    question = MagicMock(spec=Question)
    question.id = 1
    question.text = "Test question"
    question.answers = [correct_answer, incorrect_answer]
    
    # Create mock quiz
    quiz = MagicMock(spec=Quiz)
    quiz.id = 1
    quiz.title = "Test Quiz"
    quiz.status = "published"
    quiz.level_id = 1
    quiz.questions = [question]
    
    return quiz

@pytest.fixture
def mock_level():
    """Mock level"""
    level = MagicMock(spec=Level)
    level.id = 1
    level.code = "beginner"
    level.description = "Beginner"
    level.level = 1
    return level

@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    with patch("app.services.quiz_service.AIService") as mock_service:
        # Setup the mock
        instance = mock_service.return_value
        instance.generate_explanation = AsyncMock(return_value="This is the explanation")
        yield instance

@pytest.mark.asyncio
async def test_check_answer_correct(mock_db, mock_student_user, mock_quiz_with_questions, mock_level, mock_ai_service):
    """Test checking a correct answer"""
    # Arrange
    quiz_service = QuizService()
    
    # Mock get_quiz_by_id
    quiz_service.get_quiz_by_id = AsyncMock(return_value=mock_quiz_with_questions)
    
    # Mock db.execute for level query
    mock_execute_result = AsyncMock()
    mock_execute_result.scalar_one_or_none = MagicMock(return_value=mock_level)
    mock_db.execute.return_value = mock_execute_result
    
    # Create answer check data - correct answer (id=1)
    answer_check_data = AnswerCheck(question_id=1, answer_id=1)
    
    # Act
    result = await quiz_service.check_answer(
        db=mock_db,
        quiz_id=1,
        answer_check_data=answer_check_data,
        current_user=mock_student_user
    )
    
    # Assert
    assert result.is_correct == True
    assert result.correct_answer_id == 1
    assert result.explanation == "This is the explanation"
    
    # Verify AI service call
    mock_ai_service.generate_explanation.assert_called_once()
    args, kwargs = mock_ai_service.generate_explanation.call_args
    assert kwargs["is_student_correct"] == True
    assert kwargs["student_answer_text"] is None  # No wrong answer text needed

@pytest.mark.asyncio
async def test_check_answer_incorrect(mock_db, mock_student_user, mock_quiz_with_questions, mock_level, mock_ai_service):
    """Test checking an incorrect answer"""
    # Arrange
    quiz_service = QuizService()
    
    # Mock get_quiz_by_id
    quiz_service.get_quiz_by_id = AsyncMock(return_value=mock_quiz_with_questions)
    
    # Mock db.execute for level query
    mock_execute_result = AsyncMock()
    mock_execute_result.scalar_one_or_none = MagicMock(return_value=mock_level)
    mock_db.execute.return_value = mock_execute_result
    
    # Create answer check data - incorrect answer (id=2)
    answer_check_data = AnswerCheck(question_id=1, answer_id=2)
    
    # Act
    result = await quiz_service.check_answer(
        db=mock_db,
        quiz_id=1,
        answer_check_data=answer_check_data,
        current_user=mock_student_user
    )
    
    # Assert
    assert result.is_correct == False
    assert result.correct_answer_id == 1
    assert result.explanation == "This is the explanation"
    
    # Verify AI service call
    mock_ai_service.generate_explanation.assert_called_once()
    args, kwargs = mock_ai_service.generate_explanation.call_args
    assert kwargs["is_student_correct"] == False
    assert kwargs["student_answer_text"] == "Incorrect answer"  # Wrong answer text provided

@pytest.mark.asyncio
async def test_check_answer_admin_forbidden(mock_db, mock_admin_user):
    """Test admin cannot check answers"""
    # Arrange
    quiz_service = QuizService()
    answer_check_data = AnswerCheck(question_id=1, answer_id=1)
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await quiz_service.check_answer(
            db=mock_db,
            quiz_id=1,
            answer_check_data=answer_check_data,
            current_user=mock_admin_user
        )
    
    assert excinfo.value.status_code == 403
    assert "Only students can check answers" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_check_answer_quiz_not_published(mock_db, mock_student_user):
    """Test checking answer for unpublished quiz"""
    # Arrange
    quiz_service = QuizService()
    
    # Create draft quiz
    draft_quiz = MagicMock(spec=Quiz)
    draft_quiz.id = 1
    draft_quiz.status = "draft"
    
    # Mock get_quiz_by_id
    quiz_service.get_quiz_by_id = AsyncMock(return_value=draft_quiz)
    
    answer_check_data = AnswerCheck(question_id=1, answer_id=1)
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await quiz_service.check_answer(
            db=mock_db,
            quiz_id=1,
            answer_check_data=answer_check_data,
            current_user=mock_student_user
        )
    
    assert excinfo.value.status_code == 404
    assert "Quiz not found or not published" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_check_answer_question_not_found(mock_db, mock_student_user, mock_quiz_with_questions):
    """Test checking answer for non-existent question"""
    # Arrange
    quiz_service = QuizService()
    
    # Mock get_quiz_by_id
    quiz_service.get_quiz_by_id = AsyncMock(return_value=mock_quiz_with_questions)
    
    # Non-existent question ID
    answer_check_data = AnswerCheck(question_id=999, answer_id=1)
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await quiz_service.check_answer(
            db=mock_db,
            quiz_id=1,
            answer_check_data=answer_check_data,
            current_user=mock_student_user
        )
    
    assert excinfo.value.status_code == 404
    assert "Question not found in this quiz" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_check_answer_answer_not_found(mock_db, mock_student_user, mock_quiz_with_questions):
    """Test checking non-existent answer"""
    # Arrange
    quiz_service = QuizService()
    
    # Mock get_quiz_by_id
    quiz_service.get_quiz_by_id = AsyncMock(return_value=mock_quiz_with_questions)
    
    # Valid question ID but non-existent answer ID
    answer_check_data = AnswerCheck(question_id=1, answer_id=999)
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await quiz_service.check_answer(
            db=mock_db,
            quiz_id=1,
            answer_check_data=answer_check_data,
            current_user=mock_student_user
        )
    
    assert excinfo.value.status_code == 404
    assert "Answer not found for this question" in str(excinfo.value.detail) 