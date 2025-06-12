from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.level import Level

async def get_level(db: AsyncSession, level_id: int) -> Optional[Level]:
    """
    Get a level by ID
    
    Args:
        db: Database session
        level_id: ID of the level
        
    Returns:
        Level object or None if not found
    """
    query = select(Level).where(Level.id == level_id)
    result = await db.execute(query)
    return result.scalars().first()

async def get_level_by_code(db: AsyncSession, code: str) -> Optional[Level]:
    """
    Get a level by code
    
    Args:
        db: Database session
        code: Level code
        
    Returns:
        Level object or None if not found
    """
    query = select(Level).where(Level.code == code)
    result = await db.execute(query)
    return result.scalars().first()

async def get_levels(db: AsyncSession) -> List[Level]:
    """
    Get all levels
    
    Args:
        db: Database session
        
    Returns:
        List of level objects
    """
    query = select(Level).order_by(Level.level)
    result = await db.execute(query)
    return result.scalars().all()

async def create_level(
    db: AsyncSession,
    *,
    code: str,
    description: str,
    level: int
) -> Level:
    """
    Create a new level
    
    Args:
        db: Database session
        code: Level code
        description: Level description
        level: Level number
        
    Returns:
        Created level object
    """
    level_obj = Level(
        code=code,
        description=description,
        level=level
    )
    
    db.add(level_obj)
    await db.flush()
    
    return level_obj 