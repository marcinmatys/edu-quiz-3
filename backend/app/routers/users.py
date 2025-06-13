from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas.user import UserRead
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(tags=["Users"])

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user profile.
    
    This endpoint returns the profile information of the currently authenticated user,
    based on the JWT token provided in the Authorization header.
    
    Returns:
        UserRead: User profile information excluding sensitive data
    """
    return current_user 