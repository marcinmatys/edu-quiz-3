import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ...services.quiz_service import QuizService
from ...services.ai_quiz_generator import AIGenerationError
from ...schemas.quiz import QuizCreate, QuizReadList, QuizUpdate
from ...schemas.question import QuestionCreate, QuestionCreateOrUpdate
from ...schemas.answer import AnswerCreate, AnswerCreateOrUpdate
from ...models.user import User
from ...models.quiz import Quiz
from ...models.question import Question
from ...models.result import Result
from ...models.level import Level
from ...models.answer import Answer

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
def mock_student_user():
    """Mock student user"""
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "student"
    user.role = "student"
    user.is_active = True
    return user

@pytest.fixture
def mock_execute_result():
    """Mock result from db.execute()"""
    # Create mock quiz objects
    quiz1 = MagicMock(spec=Quiz)
    quiz1.id = 1
    quiz1.title = "Published Quiz"
    quiz1.status = "published"
    quiz1.level_id = 1
    quiz1.creator_id = 1
    quiz1.updated_at = "2023-06-15T12:00:00"
    
    quiz2 = MagicMock(spec=Quiz)
    quiz2.id = 2
    quiz2.title = "Draft Quiz"
    quiz2.status = "draft"
    quiz2.level_id = 2
    quiz2.creator_id = 1
    quiz2.updated_at = "2023-06-16T12:00:00"
    
    # Create mock result object
    result = MagicMock(spec=Result)
    result.score = 8
    result.max_score = 10
    result.user_id = 2
    result.quiz_id = 1
    
    # Create mock rows for different scenarios
    published_row_with_result = (quiz1, 10, result)
    published_row_no_result = (quiz1, 10, None)
    draft_row = (quiz2, 5, None)
    
    # Create mock result object that can be iterated
    mock_result = MagicMock()
    
    # Different configurations for different test cases
    # Will be set in individual tests
    mock_result.__iter__.return_value = []
    
    return {
        "mock_result": mock_result,
        "published_row_with_result": published_row_with_result,
        "published_row_no_result": published_row_no_result,
        "draft_row": draft_row
    }

@pytest.fixture
def mock_update_quiz_data():
    """Mock data for quiz update"""
    return QuizUpdate(
        title="Updated Quiz Title",
        level_id=2,
        status="published",
        questions=[
            # Existing question with updates
            QuestionCreateOrUpdate(
                id=1,
                text="Updated Question 1",
                answers=[
                    # Existing answer with updates
                    AnswerCreateOrUpdate(
                        id=1,
                        text="Updated Answer 1",
                        is_correct=True
                    ),
                    # New answer
                    AnswerCreateOrUpdate(
                        text="New Answer",
                        is_correct=False
                    )
                ]
            ),
            # New question
            QuestionCreateOrUpdate(
                text="New Question",
                answers=[
                    AnswerCreateOrUpdate(
                        text="New Question Answer 1",
                        is_correct=True
                    ),
                    AnswerCreateOrUpdate(
                        text="New Question Answer 2",
                        is_correct=False
                    )
                ]
            )
        ]
    )

@pytest.mark.asyncio
async def test_get_quizzes_admin_all_quizzes(mock_db, mock_admin_user, mock_execute_result):
    """Test getting all quizzes as admin"""
    # Arrange
    service = QuizService()
    
    # Setup mock db.execute to return both published and draft quizzes
    mock_execute_result["mock_result"].__iter__.return_value = [
        mock_execute_result["published_row_no_result"],
        mock_execute_result["draft_row"]
    ]
    mock_db.execute.return_value = mock_execute_result["mock_result"]
    
    # Act
    result = await service.get_quizzes(
        db=mock_db,
        user=mock_admin_user,
        sort_by="title",
        order="asc"
    )
    
    # Assert
    assert len(result) == 2
    assert result[0].status == "published"
    assert result[1].status == "draft"
    assert result[0].question_count == 10
    assert result[1].question_count == 5
    assert result[0].last_result is None
    assert result[1].last_result is None
    
    # Verify query was constructed correctly
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_quizzes_admin_filter_by_status(mock_db, mock_admin_user, mock_execute_result):
    """Test getting quizzes filtered by status as admin"""
    # Arrange
    service = QuizService()
    
    # Setup mock db.execute to return only draft quizzes
    mock_execute_result["mock_result"].__iter__.return_value = [
        mock_execute_result["draft_row"]
    ]
    mock_db.execute.return_value = mock_execute_result["mock_result"]
    
    # Act
    result = await service.get_quizzes(
        db=mock_db,
        user=mock_admin_user,
        sort_by="title",
        order="asc",
        status="draft"
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].status == "draft"
    assert result[0].question_count == 5
    
    # Verify query was constructed correctly
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_quizzes_student_only_published(mock_db, mock_student_user, mock_execute_result):
    """Test that students can only see published quizzes"""
    # Arrange
    service = QuizService()
    
    # Setup mock db.execute to return only published quizzes
    mock_execute_result["mock_result"].__iter__.return_value = [
        mock_execute_result["published_row_with_result"]
    ]
    mock_db.execute.return_value = mock_execute_result["mock_result"]
    
    # Act
    result = await service.get_quizzes(
        db=mock_db,
        user=mock_student_user,
        sort_by="level",
        order="desc"
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].status == "published"
    assert result[0].question_count == 10
    assert result[0].last_result is not None
    assert result[0].last_result.score == 8
    assert result[0].last_result.max_score == 10
    
    # Verify query was constructed correctly
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_quizzes_student_ignores_status_filter(mock_db, mock_student_user, mock_execute_result):
    """Test that status filter is ignored for students"""
    # Arrange
    service = QuizService()
    
    # Setup mock db.execute to return only published quizzes
    mock_execute_result["mock_result"].__iter__.return_value = [
        mock_execute_result["published_row_no_result"]
    ]
    mock_db.execute.return_value = mock_execute_result["mock_result"]
    
    # Act
    # Try to filter by draft status as student (should be ignored)
    result = await service.get_quizzes(
        db=mock_db,
        user=mock_student_user,
        sort_by="title",
        order="asc",
        status="draft"  # This should be ignored
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].status == "published"
    
    # Verify query was constructed correctly
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_quizzes_invalid_sort_by(mock_db, mock_admin_user):
    """Test invalid sort_by parameter"""
    # Arrange
    service = QuizService()
    
    # Act / Assert
    with pytest.raises(ValueError) as exc_info:
        await service.get_quizzes(
            db=mock_db,
            user=mock_admin_user,
            sort_by="invalid_field",  # Invalid sort_by
            order="asc"
        )
    
    assert "Invalid sort_by parameter" in str(exc_info.value)
    assert not mock_db.execute.called

@pytest.mark.asyncio
async def test_get_quizzes_invalid_order(mock_db, mock_admin_user):
    """Test invalid order parameter"""
    # Arrange
    service = QuizService()
    
    # Act / Assert
    with pytest.raises(ValueError) as exc_info:
        await service.get_quizzes(
            db=mock_db,
            user=mock_admin_user,
            sort_by="title",
            order="invalid_order"  # Invalid order
        )
    
    assert "Invalid order parameter" in str(exc_info.value)
    assert not mock_db.execute.called

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
    """Test creating AI quiz with database error"""
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

@pytest.mark.asyncio
async def test_get_quiz_by_id_success(mock_db):
    """Test getting a quiz by ID successfully"""
    # Arrange
    service = QuizService()
    
    # Create mock quiz with questions and answers
    mock_answer1 = MagicMock(spec=Answer)
    mock_answer1.id = 1
    mock_answer1.text = "Answer 1"
    mock_answer1.is_correct = 1
    
    mock_answer2 = MagicMock(spec=Answer)
    mock_answer2.id = 2
    mock_answer2.text = "Answer 2"
    mock_answer2.is_correct = 0
    
    mock_question = MagicMock(spec=Question)
    mock_question.id = 1
    mock_question.text = "Test Question"
    mock_question.answers = [mock_answer1, mock_answer2]
    
    mock_quiz = MagicMock(spec=Quiz)
    mock_quiz.id = 1
    mock_quiz.title = "Test Quiz"
    mock_quiz.status = "published"
    mock_quiz.level_id = 1
    mock_quiz.creator_id = 1
    mock_quiz.questions = [mock_question]
    
    # Setup mock result
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_quiz
    mock_db.execute.return_value = mock_result
    
    # Act
    result = await service.get_quiz_by_id(db=mock_db, quiz_id=1)
    
    # Assert
    assert result is not None
    assert result.id == 1
    assert result.title == "Test Quiz"
    assert len(result.questions) == 1
    assert result.questions[0].id == 1
    assert len(result.questions[0].answers) == 2
    
    # Verify query was constructed correctly
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_quiz_by_id_not_found(mock_db):
    """Test getting a quiz by ID that doesn't exist"""
    # Arrange
    service = QuizService()
    
    # Setup mock result
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_quiz_by_id(db=mock_db, quiz_id=999)
    
    # Verify exception details
    assert excinfo.value.status_code == 404
    assert "Quiz not found" in excinfo.value.detail
    
    # Verify query was constructed correctly
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_quiz_success(mock_db, mock_crud):
    """Test successful quiz update"""
    # Arrange
    service = QuizService()
    quiz_id = 1
    quiz_data = mock_update_quiz_data()
    
    # Setup mocks
    mock_db.flush = AsyncMock()
    
    # Mock get_quiz to return existing quiz
    with patch("app.services.quiz_service.get_quiz", return_value=mock_crud["mock_quiz_with_relations"]) as mock_get_quiz:
        # Mock get_level to return existing level
        with patch("app.services.quiz_service.get_level", return_value=mock_crud["mock_level"]) as mock_get_level:
            # Mock get_questions_by_quiz to return existing questions
            with patch("app.services.quiz_service.get_questions_by_quiz") as mock_get_questions:
                mock_question = MagicMock()
                mock_question.id = 1
                mock_get_questions.return_value = [mock_question]
                
                # Mock delete_questions_by_ids
                with patch("app.services.quiz_service.delete_questions_by_ids") as mock_delete_questions:
                    # Mock update_question_with_answers
                    with patch.object(service, "update_question_with_answers") as mock_update_question:
                        # Mock create_question_with_answers
                        with patch.object(service, "create_question_with_answers") as mock_create_question:
                            # Act
                            result = await service.update_quiz(
                                db=mock_db,
                                quiz_id=quiz_id,
                                quiz_data=quiz_data
                            )
                            
                            # Assert
                            assert result == mock_crud["mock_quiz_with_relations"]
                            assert mock_crud["mock_quiz_with_relations"].title == quiz_data.title
                            assert mock_crud["mock_quiz_with_relations"].level_id == quiz_data.level_id
                            assert mock_crud["mock_quiz_with_relations"].status == quiz_data.status
                            
                            # Verify get_quiz was called
                            mock_get_quiz.assert_called_once_with(mock_db, quiz_id)
                            
                            # Verify get_level was called
                            mock_get_level.assert_called_once_with(mock_db, quiz_data.level_id)
                            
                            # Verify get_questions_by_quiz was called
                            mock_get_questions.assert_called_once_with(mock_db, quiz_id)
                            
                            # Verify no questions were deleted (since all existing questions were in the update)
                            mock_delete_questions.assert_not_called()
                            
                            # Verify update_question_with_answers was called for existing question
                            mock_update_question.assert_called_once_with(mock_db, quiz_data.questions[0])
                            
                            # Verify create_question_with_answers was called for new question
                            mock_create_question.assert_called_once_with(mock_db, quiz_id, quiz_data.questions[1])
                            
                            # Verify db.flush was called
                            mock_db.flush.assert_called_once()

@pytest.mark.asyncio
async def test_update_quiz_not_found(mock_db):
    """Test quiz update when quiz not found"""
    # Arrange
    service = QuizService()
    quiz_id = 999  # Non-existent quiz
    quiz_data = mock_update_quiz_data()
    
    # Mock get_quiz to return None
    with patch("app.services.quiz_service.get_quiz", return_value=None):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.update_quiz(
                db=mock_db,
                quiz_id=quiz_id,
                quiz_data=quiz_data
            )
        
        assert exc_info.value.status_code == 404
        assert f"Quiz with ID {quiz_id} not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_update_quiz_level_not_found(mock_db, mock_crud):
    """Test quiz update when level not found"""
    # Arrange
    service = QuizService()
    quiz_id = 1
    quiz_data = mock_update_quiz_data()
    
    # Mock get_quiz to return existing quiz
    with patch("app.services.quiz_service.get_quiz", return_value=mock_crud["mock_quiz_with_relations"]):
        # Mock get_level to return None (level not found)
        with patch("app.services.quiz_service.get_level", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await service.update_quiz(
                    db=mock_db,
                    quiz_id=quiz_id,
                    quiz_data=quiz_data
                )
            
            assert exc_info.value.status_code == 404
            assert f"Level with ID {quiz_data.level_id} not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_update_quiz_database_error(mock_db, mock_crud):
    """Test quiz update when database error occurs"""
    # Arrange
    service = QuizService()
    quiz_id = 1
    quiz_data = mock_update_quiz_data()
    
    # Mock get_quiz to return existing quiz
    with patch("app.services.quiz_service.get_quiz", return_value=mock_crud["mock_quiz_with_relations"]):
        # Mock get_level to return existing level
        with patch("app.services.quiz_service.get_level", return_value=mock_crud["mock_level"]):
            # Mock get_questions_by_quiz to raise SQLAlchemyError
            with patch("app.services.quiz_service.get_questions_by_quiz", side_effect=SQLAlchemyError("Database error")):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    await service.update_quiz(
                        db=mock_db,
                        quiz_id=quiz_id,
                        quiz_data=quiz_data
                    )
                
                assert exc_info.value.status_code == 500
                assert "An error occurred while updating the quiz" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_update_question_with_answers(mock_db):
    """Test updating a question with its answers"""
    # Arrange
    service = QuizService()
    question_data = QuestionCreateOrUpdate(
        id=1,
        text="Updated Question",
        answers=[
            # Existing answer with update
            AnswerCreateOrUpdate(
                id=1,
                text="Updated Answer 1",
                is_correct=True
            ),
            # New answer
            AnswerCreateOrUpdate(
                text="New Answer",
                is_correct=False
            )
        ]
    )
    
    # Mock get_answers_by_question
    with patch("app.services.quiz_service.get_answers_by_question") as mock_get_answers:
        mock_answer = MagicMock()
        mock_answer.id = 1
        mock_get_answers.return_value = [mock_answer]
        
        # Mock delete_answers_by_ids
        with patch("app.services.quiz_service.delete_answers_by_ids") as mock_delete_answers:
            # Mock update_question
            with patch("app.services.quiz_service.update_question") as mock_update_question:
                mock_question = MagicMock()
                mock_question.id = 1
                mock_update_question.return_value = mock_question
                
                # Mock update_answer
                with patch("app.services.quiz_service.update_answer") as mock_update_answer:
                    # Mock create_answer
                    with patch("app.services.quiz_service.create_answer") as mock_create_answer:
                        # Act
                        result = await service.update_question_with_answers(
                            db=mock_db,
                            question_data=question_data
                        )
                        
                        # Assert
                        assert result == mock_question
                        
                        # Verify get_answers_by_question was called
                        mock_get_answers.assert_called_once_with(mock_db, question_data.id)
                        
                        # Verify delete_answers_by_ids was not called (no answers to delete)
                        mock_delete_answers.assert_not_called()
                        
                        # Verify update_question was called
                        mock_update_question.assert_called_once_with(
                            mock_db, 
                            question_id=question_data.id, 
                            question_data=question_data
                        )
                        
                        # Verify update_answer was called for existing answer
                        mock_update_answer.assert_called_once_with(
                            mock_db,
                            answer_id=question_data.answers[0].id,
                            answer_data=question_data.answers[0]
                        )
                        
                        # Verify create_answer was called for new answer
                        mock_create_answer.assert_called_once_with(
                            mock_db,
                            question_id=question_data.id,
                            answer_data=question_data.answers[1]
                        )

@pytest.mark.asyncio
async def test_update_question_with_answers_delete_answers(mock_db):
    """Test updating a question with deletion of answers"""
    # Arrange
    service = QuizService()
    question_data = QuestionCreateOrUpdate(
        id=1,
        text="Updated Question",
        answers=[
            # Only one answer in the update
            AnswerCreateOrUpdate(
                id=1,
                text="Updated Answer 1",
                is_correct=True
            )
        ]
    )
    
    # Mock get_answers_by_question to return two answers (one will be deleted)
    with patch("app.services.quiz_service.get_answers_by_question") as mock_get_answers:
        mock_answer1 = MagicMock()
        mock_answer1.id = 1
        mock_answer2 = MagicMock()
        mock_answer2.id = 2  # This one will be deleted
        mock_get_answers.return_value = [mock_answer1, mock_answer2]
        
        # Mock delete_answers_by_ids
        with patch("app.services.quiz_service.delete_answers_by_ids") as mock_delete_answers:
            # Mock update_question
            with patch("app.services.quiz_service.update_question") as mock_update_question:
                mock_question = MagicMock()
                mock_question.id = 1
                mock_update_question.return_value = mock_question
                
                # Mock update_answer
                with patch("app.services.quiz_service.update_answer") as mock_update_answer:
                    # Act
                    result = await service.update_question_with_answers(
                        db=mock_db,
                        question_data=question_data
                    )
                    
                    # Assert
                    assert result == mock_question
                    
                    # Verify get_answers_by_question was called
                    mock_get_answers.assert_called_once_with(mock_db, question_data.id)
                    
                    # Verify delete_answers_by_ids was called with ID 2
                    mock_delete_answers.assert_called_once_with(mock_db, [2])
                    
                    # Verify update_question was called
                    mock_update_question.assert_called_once_with(
                        mock_db, 
                        question_id=question_data.id, 
                        question_data=question_data
                    )
                    
                    # Verify update_answer was called for existing answer
                    mock_update_answer.assert_called_once_with(
                        mock_db,
                        answer_id=question_data.answers[0].id,
                        answer_data=question_data.answers[0]
                    )

@pytest.mark.asyncio
async def test_create_question_with_answers(mock_db):
    """Test creating a new question with answers"""
    # Arrange
    service = QuizService()
    quiz_id = 1
    question_data = QuestionCreateOrUpdate(
        text="New Question",
        answers=[
            AnswerCreateOrUpdate(
                text="Answer 1",
                is_correct=True
            ),
            AnswerCreateOrUpdate(
                text="Answer 2",
                is_correct=False
            )
        ]
    )
    
    # Mock create_question
    with patch("app.services.quiz_service.create_question") as mock_create_question:
        mock_question = MagicMock()
        mock_question.id = 1
        mock_create_question.return_value = mock_question
        
        # Act
        result = await service.create_question_with_answers(
            db=mock_db,
            quiz_id=quiz_id,
            question_data=question_data
        )
        
        # Assert
        assert result == mock_question
        
        # Verify create_question was called with converted QuestionCreate
        mock_create_question.assert_called_once()
        args, kwargs = mock_create_question.call_args
        assert kwargs["quiz_id"] == quiz_id
        assert isinstance(kwargs["question_data"], QuestionCreate)
        assert kwargs["question_data"].text == question_data.text
        assert len(kwargs["question_data"].answers) == 2
        assert isinstance(kwargs["question_data"].answers[0], AnswerCreate)
        assert kwargs["question_data"].answers[0].text == question_data.answers[0].text
        assert kwargs["question_data"].answers[0].is_correct == question_data.answers[0].is_correct 