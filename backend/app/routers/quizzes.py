from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Literal
import logging

from ..db import get_db
from ..core.security import get_current_active_admin, get_current_active_user
from ..services.quiz_service import QuizService
from ..services.ai_quiz_generator import AIGenerationError
from ..schemas.quiz import (
    QuizCreate, QuizGenerationResponse, QuizReadList, 
    QuizReadDetail, QuizReadDetailStudent
)
from ..models.user import User
from ..crud.quiz import get_quizzes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/quizzes", tags=["quizzes"])

# Initialize services
quiz_service = QuizService()

@router.get(
    "/",
    response_model=List[QuizReadList],
    status_code=status.HTTP_200_OK,
    summary="Get list of quizzes",
    description="Get list of quizzes. Admins can see all quizzes and filter by status, students can only see published quizzes."
)
async def list_quizzes(
    sort_by: Literal["level", "title", "updated_at"] = Query("level", description="Field to sort by"),
    order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
    status: Optional[Literal["draft", "published"]] = Query(None, description="Filter by status (admin only)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of quizzes
    
    - **sort_by**: Field to sort by (level, title, updated_at)
    - **order**: Sort order (asc, desc)
    - **status**: Filter by status (admin only)
    
    Admins can see all quizzes and filter by status.
    Students can only see published quizzes.
    """
    try:
        quizzes = await quiz_service.get_quizzes(
            db=db,
            user=current_user,
            sort_by=sort_by,
            order=order,
            status=status
        )
        return quizzes
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error during quiz listing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Unexpected error during quiz listing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post(
    "/", 
    response_model=QuizGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quiz with AI generation",
    description="Generate a new quiz with questions and answers using AI. Only admin users can create quizzes."
)
async def create_quiz(
    quiz_data: QuizCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create a new quiz with AI generation
    
    - **topic**: Topic of the quiz
    - **question_count**: Number of questions (5-20)
    - **level_id**: ID of the difficulty level
    
    Only admin users can use this endpoint.
    """

    print(f"quiz_data========================: {quiz_data}")
    try:
        quiz = await quiz_service.create_ai_quiz(
            db=db,
            quiz_data=quiz_data,
            creator_id=current_user.id
        )
        return quiz
    except ValueError as e:
        # Handle validation errors (e.g., invalid level_id)
        logger.warning(f"Validation error during quiz creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except AIGenerationError as e:
        # Handle AI generation errors
        logger.error(f"AI generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error generating quiz with AI: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Unexpected error during quiz creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

# Additional endpoints for quiz operations can be added here
# For example:
# - GET / - Get list of quizzes
# - GET /{quiz_id} - Get a specific quiz
# - PUT /{quiz_id} - Update a quiz
# - DELETE /{quiz_id} - Delete a quiz
# - etc. 