from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from app.db import get_db
from app.models import User, Level, Quiz, Question, Answer, Result

router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    responses={404: {"description": "Not found"}},
)

@router.get("/tables")
def get_tables(db: Session = Depends(get_db)):
    """Get a list of all tables in the database"""
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    return {"tables": tables}

@router.get("/schema/{table_name}")
def get_schema(table_name: str, db: Session = Depends(get_db)):
    """Get the schema of a specific table"""
    inspector = inspect(db.bind)
    if table_name not in inspector.get_table_names():
        return {"error": f"Table '{table_name}' not found"}
    
    columns = inspector.get_columns(table_name)
    return {"table": table_name, "columns": columns}

@router.get("/data/{table_name}")
def get_table_data(table_name: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get data from a specific table"""
    inspector = inspect(db.bind)
    if table_name not in inspector.get_table_names():
        return {"error": f"Table '{table_name}' not found"}
    
    # Use raw SQL to be table-agnostic
    result = db.execute(text(f"SELECT * FROM {table_name} LIMIT :limit"), {"limit": limit})
    rows = [dict(row._mapping) for row in result]
    
    # Get total count
    count_result = db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
    total = dict(count_result.first()._mapping)["count"]
    
    return {
        "table": table_name,
        "total_rows": total,
        "limit": limit,
        "data": rows
    }

# Model-specific endpoints for more detailed information

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return [{"id": user.id, "username": user.username, "role": user.role} for user in users]

@router.get("/levels")
def get_levels(db: Session = Depends(get_db)):
    """Get all levels"""
    levels = db.query(Level).all()
    return [{"id": level.id, "code": level.code, "description": level.description, "level": level.level} for level in levels]

@router.get("/quizzes")
def get_quizzes(db: Session = Depends(get_db)):
    """Get all quizzes with basic information"""
    quizzes = db.query(Quiz).all()
    return [{"id": quiz.id, "title": quiz.title, "status": quiz.status, "level_id": quiz.level_id} for quiz in quizzes]

@router.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific quiz including questions and answers"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return {"error": f"Quiz with ID {quiz_id} not found"}
    
    questions = []
    for question in quiz.questions:
        answers = [{"id": answer.id, "text": answer.text, "is_correct": bool(answer.is_correct)} 
                  for answer in question.answers]
        questions.append({
            "id": question.id,
            "text": question.text,
            "answers": answers
        })
    
    return {
        "id": quiz.id,
        "title": quiz.title,
        "status": quiz.status,
        "level": {
            "id": quiz.level.id,
            "code": quiz.level.code,
            "description": quiz.level.description
        },
        "creator": {
            "id": quiz.creator.id,
            "username": quiz.creator.username
        },
        "questions": questions
    } 