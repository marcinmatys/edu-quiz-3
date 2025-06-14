import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import joinedload, aliased, selectinload

from ..crud.quiz import create_quiz, get_quiz, get_quizzes
from ..crud.question import create_question
from ..crud.answer import create_answer
from ..crud.level import get_level
from ..models.quiz import Quiz
from ..models.question import Question
from ..models.result import Result
from ..models.level import Level
from ..models.user import User
from ..schemas.quiz import QuizCreate, QuizGenerationResponse, QuizReadList
from ..schemas.question import QuestionCreate
from ..schemas.answer import AnswerCreate
from ..services.ai_quiz_generator import AIQuizGeneratorService, AIGenerationError
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class QuizService:
    """Service for quiz operations"""
    
    def __init__(self):
        """Initialize the quiz service"""
        self.ai_generator = AIQuizGeneratorService()
    
    async def get_quiz_by_id(self, db: AsyncSession, quiz_id: int) -> Quiz:
        """
        Get a quiz by ID with all related questions and answers
        
        Args:
            db: Database session
            quiz_id: ID of the quiz to retrieve
            
        Returns:
            Quiz object with loaded relationships
            
        Raises:
            HTTPException: If quiz not found (404)
        """
        # Build query with selectinload to efficiently load related data
        query = select(Quiz).where(Quiz.id == quiz_id).options(
            selectinload(Quiz.questions).selectinload(Question.answers)
        )
        
        # Execute query
        result = await db.execute(query)
        quiz = result.scalar_one_or_none()
        
        # Raise 404 if quiz not found
        if not quiz:
            logger.warning(f"Quiz with ID {quiz_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
            
        return quiz
    
    async def get_quizzes(
        self,
        db: AsyncSession,
        user: User,
        sort_by: str = "level",
        order: str = "asc",
        status: Optional[str] = None
    ) -> List[QuizReadList]:
        """
        Get list of quizzes based on user role and filters
        
        Args:
            db: Database session
            user: Current user
            sort_by: Field to sort by (level, title, updated_at)
            order: Sort order (asc, desc)
            status: Filter by status (admin only)
            
        Returns:
            List of quizzes with question count and optional last result
            
        Raises:
            ValueError: If sort_by or order parameters are invalid
        """
        # Validate sort_by parameter
        if sort_by not in ["level", "title", "updated_at"]:
            raise ValueError(f"Invalid sort_by parameter: {sort_by}")
            
        # Validate order parameter
        if order not in ["asc", "desc"]:
            raise ValueError(f"Invalid order parameter: {order}")
        
        # Start building the query
        query = select(Quiz)
        
        # Add question count subquery
        question_count = (
            select(func.count(Question.id))
            .where(Question.quiz_id == Quiz.id)
            .scalar_subquery()
            .label("question_count")
        )
        
        query = query.add_columns(question_count)
        
        # For students, only show published quizzes
        # For admins, show all quizzes or filter by status if provided
        if user.role == "student":
            query = query.where(Quiz.status == "published")
        elif status:
            query = query.where(Quiz.status == status)
        
        # Add last_result for students
        last_result = None
        if user.role == "student":
            # Use aliased to avoid ambiguity
            result_alias = aliased(Result)
            query = query.outerjoin(
                result_alias, 
                (result_alias.quiz_id == Quiz.id) & (result_alias.user_id == user.id)
            )
            query = query.add_columns(result_alias)
        
        # Add joins for sorting
        if sort_by == "level":
            query = query.join(Level, Quiz.level_id == Level.id)
            sort_column = Level.level
        elif sort_by == "title":
            sort_column = Quiz.title
        else:  # updated_at
            sort_column = Quiz.updated_at
        
        # Apply sorting
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Execute query
        result = await db.execute(query)
        
        # Process results
        quiz_list = []
        for row in result:
            quiz = row[0]  # Quiz object
            question_count = row[1]  # question_count value
            
            # Create quiz dict with question_count
            quiz_dict = {
                "id": quiz.id,
                "title": quiz.title,
                "status": quiz.status,
                "level_id": quiz.level_id,
                "creator_id": quiz.creator_id,
                "updated_at": quiz.updated_at,
                "question_count": question_count
            }
            
            # Add last_result for students if available
            if user.role == "student" and row[2] is not None:
                result_obj = row[2]
                quiz_dict["last_result"] = {
                    "score": result_obj.score,
                    "max_score": result_obj.max_score
                }
            
            quiz_list.append(QuizReadList.model_validate(quiz_dict))
        
        return quiz_list
    
    async def create_ai_quiz(
        self, 
        db: AsyncSession, 
        quiz_data: QuizCreate, 
        creator_id: int
    ) -> QuizGenerationResponse:
        """
        Create a quiz using AI generation
        
        Args:
            db: Database session
            quiz_data: Quiz creation data
            creator_id: ID of the user creating the quiz
            
        Returns:
            QuizGenerationResponse with the created quiz data
            
        Raises:
            ValueError: If level doesn't exist
            AIGenerationError: If AI generation fails
            SQLAlchemyError: If database operations fail
        """
        # Validate level exists
        level = await get_level(db, quiz_data.level_id)
        if not level:
            logger.error(f"Level with ID {quiz_data.level_id} not found")
            raise ValueError(f"Level with ID {quiz_data.level_id} not found")
        
        # Convert level to dict for AI service
        level_data = {
            "id": level.id,
            "code": level.code,
            "description": level.description,
            "level": level.level
        }
        
        try:
            # Generate quiz content using AI
            questions_data, title = await self.ai_generator.generate_quiz(
                quiz_data.topic, 
                quiz_data.question_count,
                level_data
            )
            
            # Create quiz record - no need to start a new transaction
            # The session is likely already in a transaction from the router
            quiz_obj = await create_quiz(
                db,
                title=title,
                level_id=quiz_data.level_id,
                creator_id=creator_id,
                status="draft"
            )
            
            # Create questions and answers
            for q_data in questions_data:
                # Create question
                question_create = QuestionCreate(
                    text=q_data["text"],
                    answers=[
                        AnswerCreate(
                            text=a["text"],
                            is_correct=a["is_correct"]
                        ) for a in q_data["answers"]
                    ]
                )
                
                question_obj = await create_question(
                    db,
                    quiz_id=quiz_obj.id,
                    question_data=question_create
                )
            
            # Explicitly commit the transaction to ensure all changes are persisted
            await db.commit()
            
            # Get complete quiz with relationships for response
            quiz_with_relations = await get_quiz(db, quiz_obj.id)
            
            return QuizGenerationResponse.model_validate(quiz_with_relations)
                
        except AIGenerationError as e:
            logger.error(f"AI generation error: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error during quiz creation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during quiz creation: {str(e)}")
            raise 