from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models.quiz import Quiz
from ..models.question import Question
from ..schemas.quiz import QuizCreate

async def create_quiz(
    db: AsyncSession,
    *,
    title: str,
    level_id: int,
    creator_id: int,
    status: str = "draft"
) -> Quiz:
    """
    Create a new quiz
    
    Args:
        db: Database session
        title: Quiz title
        level_id: ID of the level
        creator_id: ID of the user creating the quiz
        status: Quiz status (default: 'draft')
        
    Returns:
        Created quiz object
    """
    quiz = Quiz(
        title=title,
        level_id=level_id,
        creator_id=creator_id,
        status=status
    )
    
    db.add(quiz)
    await db.flush()
    
    return quiz

async def get_quiz(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
    """
    Get a quiz by ID, including related questions and answers
    
    Args:
        db: Database session
        quiz_id: ID of the quiz
        
    Returns:
        Quiz object with relationships loaded or None if not found
    """
    query = (
        select(Quiz)
        .options(
            selectinload(Quiz.questions)
            .selectinload(Question.answers)
        )
        .where(Quiz.id == quiz_id)
    )
    
    result = await db.execute(query)
    return result.scalars().first()

async def get_quizzes(
    db: AsyncSession, 
    *,
    creator_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Quiz]:
    """
    Get quizzes with optional filtering
    
    Args:
        db: Database session
        creator_id: Filter by creator ID
        status: Filter by status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of quiz objects
    """
    query = select(Quiz)
    
    if creator_id is not None:
        query = query.where(Quiz.creator_id == creator_id)
    
    if status is not None:
        query = query.where(Quiz.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_quiz_status(
    db: AsyncSession,
    *,
    quiz_id: int,
    status: str
) -> Optional[Quiz]:
    """
    Update the status of a quiz
    
    Args:
        db: Database session
        quiz_id: ID of the quiz
        status: New status
        
    Returns:
        Updated quiz object or None if not found
    """
    query = select(Quiz).where(Quiz.id == quiz_id)
    result = await db.execute(query)
    quiz = result.scalars().first()
    
    if quiz:
        quiz.status = status
        await db.flush()
        
    return quiz

async def remove_quiz(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
    """
    Remove a quiz by ID
    
    Args:
        db: Database session
        quiz_id: ID of the quiz to remove
        
    Returns:
        Removed quiz object or None if not found
    """
    quiz = await get_quiz(db, quiz_id)
    
    if quiz:
        await db.delete(quiz)
        await db.flush()
        await db.commit()
        
    return quiz 