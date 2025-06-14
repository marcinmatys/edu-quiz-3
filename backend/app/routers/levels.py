from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas.level import LevelRead
from ..crud.level import get_levels
from ..core.security import get_current_active_user, get_current_user
from ..models.user import User

router = APIRouter(
    prefix="/api/v1/levels",
    tags=["Levels"]
)

@router.get("/", response_model=List[LevelRead])
async def read_levels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available quiz difficulty levels.
    
    This endpoint returns a list of all quiz difficulty levels available in the system.
    Access is restricted to authenticated users only.
    
    Returns:
        List[LevelRead]: List of level objects with id, code, description, and level number
    """
    try:
        levels = await get_levels(db)
        return levels
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving levels"
        ) 