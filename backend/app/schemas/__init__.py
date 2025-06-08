"""Schemas package for Pydantic schemas"""

from .token import Token
from .user import UserBase, UserCreate, UserRead
from .level import LevelBase, LevelCreate, LevelRead
from .answer import (
    AnswerBase, AnswerCreate, AnswerUpdate, AnswerRead, 
    AnswerReadStudent, AnswerCheck
)
from .question import (
    QuestionBase, QuestionCreate, QuestionUpdate, 
    QuestionRead, QuestionReadStudent, AnswerCheckResponse
)
from .quiz import (
    QuizBase, QuizCreate, QuizUpdate, QuizReadBase,
    QuizReadList, QuizReadDetail, QuizReadDetailStudent,
    QuizGenerationResponse, LastResult
)
from .result import ResultBase, ResultCreate, ResultRead

__all__ = [
    # Token
    'Token',
    # User
    'UserBase', 'UserCreate', 'UserRead',
    # Level
    'LevelBase', 'LevelCreate', 'LevelRead',
    # Answer
    'AnswerBase', 'AnswerCreate', 'AnswerUpdate', 'AnswerRead', 
    'AnswerReadStudent', 'AnswerCheck',
    # Question
    'QuestionBase', 'QuestionCreate', 'QuestionUpdate', 
    'QuestionRead', 'QuestionReadStudent', 'AnswerCheckResponse',
    # Quiz
    'QuizBase', 'QuizCreate', 'QuizUpdate', 'QuizReadBase',
    'QuizReadList', 'QuizReadDetail', 'QuizReadDetailStudent',
    'QuizGenerationResponse', 'LastResult',
    # Result
    'ResultBase', 'ResultCreate', 'ResultRead'
]
