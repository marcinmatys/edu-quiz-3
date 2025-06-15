from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..models.result import Result
from ..schemas.result import ResultCreate


async def get_by_user_and_quiz(db: AsyncSession, user_id: int, quiz_id: int) -> Optional[Result]:
    """
    Get a result by user_id and quiz_id
    
    Args:
        db: Database session
        user_id: ID of the user
        quiz_id: ID of the quiz
        
    Returns:
        Result object if found, None otherwise
    """
    query = select(Result).where(
        Result.user_id == user_id,
        Result.quiz_id == quiz_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_with_owner(
    db: AsyncSession, 
    obj_in: ResultCreate, 
    user_id: int, 
    quiz_id: int
) -> Result:
    """
    Create a new result with owner
    
    Args:
        db: Database session
        obj_in: Result data
        user_id: ID of the user
        quiz_id: ID of the quiz
        
    Returns:
        Created result
    """
    result = Result(
        score=obj_in.score,
        max_score=obj_in.max_score,
        user_id=user_id,
        quiz_id=quiz_id
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)
    return result


async def update(
    db: AsyncSession, 
    db_obj: Result, 
    obj_in: ResultCreate
) -> Result:
    """
    Update a result
    
    Args:
        db: Database session
        db_obj: Existing result object
        obj_in: Updated result data
        
    Returns:
        Updated result
    """
    db_obj.score = obj_in.score
    db_obj.max_score = obj_in.max_score
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj 