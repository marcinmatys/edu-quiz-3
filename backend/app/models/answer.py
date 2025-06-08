from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, CheckConstraint, Index
from sqlalchemy.orm import relationship
from .base import Base

class Answer(Base):
    """Answer model for storing possible answers for questions"""
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(128), nullable=False)
    is_correct = Column(Integer, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship
    question = relationship("Question", back_populates="answers")
    
    # Add constraint to ensure is_correct is either 0 or 1
    __table_args__ = (
        CheckConstraint("is_correct IN (0, 1)", name="check_is_correct"),
        Index("idx_answers_question_id", "question_id"),
    )
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>" 