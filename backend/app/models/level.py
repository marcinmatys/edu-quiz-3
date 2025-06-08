from sqlalchemy import Column, Integer, String, Text
from .base import Base

class Level(Base):
    """Level model for storing predefined difficulty levels for quizzes"""
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False, unique=True)
    
    def __repr__(self):
        return f"<Level(id={self.id}, code='{self.code}', level={self.level})>" 