from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base schema for user data"""
    username: str = Field(..., min_length=3, max_length=64)
    
class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(admin|student)$")

class UserRead(UserBase):
    """Schema for reading user data"""
    id: int
    role: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True) 