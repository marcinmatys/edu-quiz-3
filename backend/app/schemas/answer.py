from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AnswerBase(BaseModel):
    """Base schema for answer data"""
    text: str = Field(..., min_length=1, max_length=128)
    
class AnswerCreate(AnswerBase):
    """Schema for answer creation"""
    is_correct: bool
    
class AnswerUpdate(AnswerBase):
    """Schema for answer update"""
    id: int
    is_correct: bool
    
class AnswerRead(AnswerBase):
    """Schema for reading answer data - admin view"""
    id: int
    is_correct: bool
    
    model_config = ConfigDict(from_attributes=True)
    
class AnswerReadStudent(AnswerBase):
    """Schema for reading answer data - student view (without is_correct)"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
class AnswerCheck(BaseModel):
    """Schema for checking an answer"""
    question_id: int
    answer_id: int 