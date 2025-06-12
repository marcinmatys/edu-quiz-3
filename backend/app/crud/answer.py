from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.answer import Answer
from ..schemas.answer import AnswerCreate, AnswerUpdate

async def create_answer(
    db: AsyncSession,
    *,
    question_id: int,
    answer_data: AnswerCreate
) -> Answer:
    """
    Create a new answer
    
    Args:
        db: Database session
        question_id: ID of the question
        answer_data: Answer data
        
    Returns:
        Created answer object
    """
    answer = Answer(
        text=answer_data.text,
        is_correct=answer_data.is_correct,
        question_id=question_id
    )
    
    db.add(answer)
    await db.flush()
    
    return answer

async def create_answers(
    db: AsyncSession,
    *,
    question_id: int,
    answers_data: List[AnswerCreate]
) -> List[Answer]:
    """
    Create multiple answers for a question
    
    Args:
        db: Database session
        question_id: ID of the question
        answers_data: List of answer data
        
    Returns:
        List of created answer objects
    """
    answers = []
    
    for answer_data in answers_data:
        answer = await create_answer(
            db,
            question_id=question_id,
            answer_data=answer_data
        )
        answers.append(answer)
    
    return answers

async def get_answer(db: AsyncSession, answer_id: int) -> Optional[Answer]:
    """
    Get an answer by ID
    
    Args:
        db: Database session
        answer_id: ID of the answer
        
    Returns:
        Answer object or None if not found
    """
    query = select(Answer).where(Answer.id == answer_id)
    result = await db.execute(query)
    return result.scalars().first()

async def get_answers_by_question(
    db: AsyncSession,
    question_id: int
) -> List[Answer]:
    """
    Get all answers for a question
    
    Args:
        db: Database session
        question_id: ID of the question
        
    Returns:
        List of answer objects
    """
    query = select(Answer).where(Answer.question_id == question_id)
    result = await db.execute(query)
    return result.scalars().all()

async def get_correct_answer(
    db: AsyncSession,
    question_id: int
) -> Optional[Answer]:
    """
    Get the correct answer for a question
    
    Args:
        db: Database session
        question_id: ID of the question
        
    Returns:
        Correct answer object or None if not found
    """
    query = select(Answer).where(
        Answer.question_id == question_id,
        Answer.is_correct == True
    )
    result = await db.execute(query)
    return result.scalars().first()

async def check_answer(
    db: AsyncSession,
    question_id: int,
    answer_id: int
) -> Tuple[bool, Optional[int]]:
    """
    Check if an answer is correct
    
    Args:
        db: Database session
        question_id: ID of the question
        answer_id: ID of the answer to check
        
    Returns:
        Tuple containing (is_correct, correct_answer_id)
    """
    # Get the correct answer
    correct_answer = await get_correct_answer(db, question_id)
    
    if not correct_answer:
        return False, None
    
    # Check if the provided answer is correct
    is_correct = correct_answer.id == answer_id
    
    return is_correct, correct_answer.id 