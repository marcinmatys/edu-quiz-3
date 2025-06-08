from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ResultBase(BaseModel):
    """Base schema for result data"""
    score: int = Field(..., ge=0)
    max_score: int = Field(..., gt=0)
    
class ResultCreate(ResultBase):
    """Schema for result creation"""
    pass
    
class ResultRead(ResultBase):
    """Schema for reading result data"""
    id: int
    user_id: int
    quiz_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True) 