from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Result(Base, TimestampMixin):
    """Result model for storing quiz results"""
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", backref="results")
    quiz = relationship("Quiz", back_populates="results")
    
    # Ensure a user can have only one result per quiz
    __table_args__ = (
        UniqueConstraint("user_id", "quiz_id", name="uix_user_quiz"),
        Index("idx_results_user_id", "user_id"),
        Index("idx_results_quiz_id", "quiz_id"),
    )
    
    def __repr__(self):
        return f"<Result(id={self.id}, user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score}/{self.max_score})>" 