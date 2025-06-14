from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import selectinload

from ..models.question import Question
from ..models.answer import Answer
from ..schemas.question import QuestionCreate, QuestionUpdate, QuestionCreateOrUpdate

async def create_question(
    db: AsyncSession,
    *,
    quiz_id: int,
    question_data: QuestionCreate
) -> Question:
    """
    Create a new question with answers
    
    Args:
        db: Database session
        quiz_id: ID of the quiz
        question_data: Question data with answers
        
    Returns:
        Created question object
    """
    # Create question
    question = Question(
        text=question_data.text,
        quiz_id=quiz_id
    )
    
    db.add(question)
    await db.flush()
    
    # Create answers for the question
    for answer_data in question_data.answers:
        answer = Answer(
            text=answer_data.text,
            is_correct=answer_data.is_correct,
            question_id=question.id
        )
        db.add(answer)
    
    await db.flush()
    return question

async def get_question(db: AsyncSession, question_id: int) -> Optional[Question]:
    """
    Get a question by ID, including related answers
    
    Args:
        db: Database session
        question_id: ID of the question
        
    Returns:
        Question object with relationships loaded or None if not found
    """
    query = (
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.id == question_id)
    )
    
    result = await db.execute(query)
    return result.scalars().first()

async def get_questions_by_quiz(
    db: AsyncSession,
    quiz_id: int
) -> List[Question]:
    """
    Get all questions for a quiz
    
    Args:
        db: Database session
        quiz_id: ID of the quiz
        
    Returns:
        List of question objects with answers
    """
    query = (
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.quiz_id == quiz_id)
    )
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_question(
    db: AsyncSession,
    *,
    question_id: int,
    question_data: QuestionUpdate
) -> Optional[Question]:
    """
    Update a question and its answers
    
    Args:
        db: Database session
        question_id: ID of the question
        question_data: Updated question data
        
    Returns:
        Updated question object or None if not found
    """
    query = select(Question).where(Question.id == question_id)
    result = await db.execute(query)
    question = result.scalars().first()
    
    if not question:
        return None
    
    # Update question
    question.text = question_data.text
    
    # Update answers
    for answer_data in question_data.answers:
        # Find answer by ID
        answer_query = select(Answer).where(
            Answer.id == answer_data.id,
            Answer.question_id == question_id
        )
        answer_result = await db.execute(answer_query)
        answer = answer_result.scalars().first()
        
        if answer:
            # Update existing answer
            answer.text = answer_data.text
            answer.is_correct = answer_data.is_correct
    
    await db.flush()
    return question

async def delete_question(
    db: AsyncSession,
    question_id: int
) -> bool:
    """
    Delete a question and all its answers
    
    Args:
        db: Database session
        question_id: ID of the question to delete
        
    Returns:
        True if deleted, False if not found
    """
    # Delete all answers for the question first
    delete_answers_query = delete(Answer).where(Answer.question_id == question_id)
    await db.execute(delete_answers_query)
    
    # Delete the question
    delete_question_query = delete(Question).where(Question.id == question_id)
    result = await db.execute(delete_question_query)
    
    return result.rowcount > 0

async def delete_questions_by_ids(
    db: AsyncSession,
    question_ids: List[int]
) -> int:
    """
    Delete multiple questions and their answers by question IDs
    
    Args:
        db: Database session
        question_ids: List of question IDs to delete
        
    Returns:
        Number of questions deleted
    """
    if not question_ids:
        return 0
    
    # Delete all answers for these questions
    delete_answers_query = delete(Answer).where(Answer.question_id.in_(question_ids))
    await db.execute(delete_answers_query)
    
    # Delete the questions
    delete_questions_query = delete(Question).where(Question.id.in_(question_ids))
    result = await db.execute(delete_questions_query)
    
    return result.rowcount 