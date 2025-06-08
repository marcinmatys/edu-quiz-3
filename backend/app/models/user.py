from sqlalchemy import Column, Integer, String, Text, CheckConstraint
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """User model for storing user account information"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True)
    hashed_password = Column(Text, nullable=False)
    role = Column(String, nullable=False)
    
    # Add constraint to ensure role is either 'admin' or 'student'
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'student')", name="check_valid_role"),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>" 