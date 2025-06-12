import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..crud.quiz import create_quiz, get_quiz
from ..crud.question import create_question
from ..crud.answer import create_answer
from ..crud.level import get_level
from ..models.quiz import Quiz
from ..schemas.quiz import QuizCreate, QuizGenerationResponse
from ..schemas.question import QuestionCreate
from ..schemas.answer import AnswerCreate
from ..services.ai_quiz_generator import AIQuizGeneratorService, AIGenerationError

logger = logging.getLogger(__name__)

class QuizService:
    """Service for quiz operations"""
    
    def __init__(self):
        """Initialize the quiz service"""
        self.ai_generator = AIQuizGeneratorService()
    
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
            
            # Start database transaction
            async with db.begin():
                # Create quiz record
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