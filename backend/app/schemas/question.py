from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union
from .answer import AnswerCreate, AnswerRead, AnswerReadStudent, AnswerUpdate, AnswerCreateOrUpdate

class QuestionBase(BaseModel):
    """Base schema for question data"""
    text: str = Field(..., min_length=5, max_length=512)
    
class QuestionCreate(QuestionBase):
    """Schema for question creation"""
    answers: List[AnswerCreate]
    
class QuestionUpdate(QuestionBase):
    """Schema for question update"""
    id: int
    answers: List[AnswerUpdate]
    
class QuestionCreateOrUpdate(QuestionBase):
    """Union schema for question creation or update in quiz update endpoint"""
    id: Optional[int] = None
    answers: List[AnswerCreateOrUpdate]
    
class QuestionReadBase(QuestionBase):
    """Base schema for reading question data"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
class QuestionRead(QuestionReadBase):
    """Schema for reading question data - admin view"""
    answers: List[AnswerRead]
    
class QuestionReadStudent(QuestionReadBase):
    """Schema for reading question data - student view"""
    answers: List[AnswerReadStudent]
    
class AnswerCheckResponse(BaseModel):
    """Schema for the response when checking an answer"""
    is_correct: bool
    correct_answer_id: int
    explanation: str 