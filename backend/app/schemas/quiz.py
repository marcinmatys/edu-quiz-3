from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from .question import QuestionCreate, QuestionRead, QuestionReadStudent, QuestionUpdate, QuestionCreateOrUpdate

class QuizBase(BaseModel):
    """Base schema for quiz data"""
    title: str = Field(..., min_length=3, max_length=256)
    level_id: int

class QuizCreate(QuizBase):
    """Schema for quiz creation via AI generation"""
    topic: str
    question_count: int = Field(..., ge=5, le=20)

class QuizUpdate(QuizBase):
    """Schema for quiz update"""
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    questions: List[QuestionCreateOrUpdate]

class QuizReadBase(QuizBase):
    """Base schema for reading quiz data"""
    id: int
    status: str
    creator_id: int
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LastResult(BaseModel):
    """Schema for displaying last quiz result in quiz list"""
    score: int
    max_score: int
    
    model_config = ConfigDict(from_attributes=True)

class QuizReadList(QuizReadBase):
    """Schema for reading quiz data in list view"""
    question_count: int
    last_result: Optional[LastResult] = None

class QuizReadDetail(QuizReadBase):
    """Schema for reading detailed quiz data - admin view"""
    questions: List[QuestionRead]

class QuizReadDetailStudent(QuizReadBase):
    """Schema for reading detailed quiz data - student view"""
    questions: List[QuestionReadStudent]

class QuizGenerationResponse(QuizReadDetail):
    """Schema for the response when generating a quiz"""
    pass 