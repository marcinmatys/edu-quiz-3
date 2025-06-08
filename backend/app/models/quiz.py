from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Quiz(Base, TimestampMixin):
    """Quiz model for storing quiz information"""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    status = Column(String, nullable=False)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    level = relationship("Level", backref="quizzes")
    creator = relationship("User", backref="created_quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="quiz", cascade="all, delete-orphan")
    
    # Add constraint to ensure status is either 'draft' or 'published'
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published')", name="check_valid_status"),
        Index("idx_quizzes_status", "status"),
        Index("idx_quizzes_level_id", "level_id")
    )
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}', status='{self.status}')>" 