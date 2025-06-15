from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Literal
import logging

from ..db import get_db
from ..core.security import get_current_active_admin, get_current_active_user, get_current_active_student
from ..services.quiz_service import QuizService
from ..services.ai_quiz_generator import AIGenerationError
from ..schemas.quiz import (
    QuizCreate, QuizGenerationResponse, QuizReadList, 
    QuizReadDetail, QuizReadDetailStudent, QuizUpdate
)
from ..schemas.question import AnswerCheckResponse
from ..schemas.answer import AnswerCheck
from ..models.user import User
from ..crud.quiz import get_quizzes, remove_quiz

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/quizzes", tags=["quizzes"])

# Initialize services
quiz_service = QuizService()

@router.get(
    "/{quiz_id}",
    status_code=status.HTTP_200_OK,
    summary="Get quiz details by ID",
    description="Get detailed information about a specific quiz. Admins receive complete data including answer correctness, while students receive the same data without answer correctness information."
)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific quiz by ID
    
    - **quiz_id**: ID of the quiz to retrieve
    
    Returns different response schemas based on user role:
    - Admins receive complete data including answer correctness (QuizReadDetail)
    - Students receive the same data without answer correctness (QuizReadDetailStudent)
    """
    try:
        # Get quiz with related questions and answers
        quiz = await quiz_service.get_quiz_by_id(db=db, quiz_id=quiz_id)
        
        # Return different response based on user role
        if current_user.role == "admin":
            # Admin view - includes answer correctness
            return QuizReadDetail.model_validate(quiz)
        else:
            # Student view - excludes answer correctness
            return QuizReadDetailStudent.model_validate(quiz)
            
    except HTTPException as e:
        # Re-raise HTTP exceptions from service
        raise e
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Unexpected error retrieving quiz {quiz_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

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

@router.put(
    "/{quiz_id}",
    response_model=QuizReadDetail,
    status_code=status.HTTP_200_OK,
    summary="Update a quiz",
    description="Update a quiz with its questions and answers. Only admin users can update quizzes."
)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update a quiz with its questions and answers
    
    - **quiz_id**: ID of the quiz to update
    - **quiz_data**: Updated quiz data including questions and answers
    
    Only admin users can use this endpoint.
    """
    try:
        quiz = await quiz_service.update_quiz(
            db=db,
            quiz_id=quiz_id,
            quiz_data=quiz_data
        )
        return QuizReadDetail.model_validate(quiz)
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error during quiz update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Unexpected error during quiz update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.delete(
    "/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a quiz",
    description="Delete a quiz with all related questions, answers, and results. Only admin users can delete quizzes."
)
async def delete_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete a quiz
    
    - **quiz_id**: ID of the quiz to delete
    
    Only admin users can use this endpoint.
    The operation is irreversible and will delete all related data.
    """
    try:
        # Check if quiz exists
        quiz = await quiz_service.get_quiz_by_id(db=db, quiz_id=quiz_id)
        
        # Delete the quiz
        await remove_quiz(db=db, quiz_id=quiz_id)
        
        # Return no content
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except HTTPException as e:
        # Re-raise HTTP exceptions from service
        raise e
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Unexpected error deleting quiz {quiz_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post(
    "/{quiz_id}/check-answer",
    response_model=AnswerCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check a student's answer to a quiz question",
    description="Check if a student's answer to a quiz question is correct. Returns correctness info and AI-generated explanation."
)
async def check_answer(
    quiz_id: int,
    answer_check_data: AnswerCheck,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_student)
):
    """
    Check if a student's answer to a quiz question is correct
    
    - **quiz_id**: ID of the quiz
    - **question_id**: ID of the question being answered
    - **answer_id**: ID of the student's selected answer
    
    Returns:
    - **is_correct**: Whether the answer is correct
    - **correct_answer_id**: ID of the correct answer
    - **explanation**: AI-generated explanation of the answer
    
    Only student users can use this endpoint.
    """
    try:
        result = await quiz_service.check_answer(
            db=db,
            quiz_id=quiz_id,
            answer_check_data=answer_check_data,
            current_user=current_user
        )
        return result
    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Unexpected error checking answer for quiz {quiz_id}: {str(e)}")
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