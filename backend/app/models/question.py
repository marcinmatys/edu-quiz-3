from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base

class Question(Base):
    """Question model for storing quiz questions"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(512), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_questions_quiz_id", "quiz_id"),
    )
    
    def __repr__(self):
        return f"<Question(id={self.id}, quiz_id={self.quiz_id})>" 