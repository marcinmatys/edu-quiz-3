from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..models.user import User

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Get a user by username
    
    Args:
        db: Database session
        username: Username to search for
        
    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID
    
    Args:
        db: Database session
        user_id: User ID to search for
        
    Returns:
        User object if found, None otherwise
    """
    return await db.get(User, user_id) 