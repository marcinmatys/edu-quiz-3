from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, Level, Quiz, Question, Answer, Result

router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    responses={404: {"description": "Not found"}},
)

@router.get("/tables")
async def get_tables(db: AsyncSession = Depends(get_db)):
    """Get a list of all tables in the database"""
    # Get the connection directly from the engine
    async with db.bind.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
    return {"tables": tables}

@router.get("/schema/{table_name}")
async def get_schema(table_name: str, db: AsyncSession = Depends(get_db)):
    """Get the schema of a specific table"""
    async with db.bind.connect() as conn:
        table_names = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        if table_name not in table_names:
            return {"error": f"Table '{table_name}' not found"}
        
        columns = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns(table_name))
    return {"table": table_name, "columns": columns}

@router.get("/data/{table_name}")
async def get_table_data(table_name: str, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get data from a specific table"""
    async with db.bind.connect() as conn:
        table_names = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        if table_name not in table_names:
            return {"error": f"Table '{table_name}' not found"}
    
    # Use raw SQL to be table-agnostic
    result = await db.execute(text(f"SELECT * FROM {table_name} LIMIT :limit"), {"limit": limit})
    rows = [dict(row._mapping) for row in result]
    
    # Get total count
    count_result = await db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
    count_row = count_result.first()
    total = dict(count_row._mapping)["count"] if count_row else 0
    
    return {
        "table": table_name,
        "total_rows": total,
        "limit": limit,
        "data": rows
    }

# Model-specific endpoints for more detailed information

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"id": user.id, "username": user.username, "role": user.role, "is_active": user.is_active} for user in users]

@router.get("/levels")
async def get_levels(db: AsyncSession = Depends(get_db)):
    """Get all levels"""
    result = await db.execute(select(Level))
    levels = result.scalars().all()
    return [{"id": level.id, "code": level.code, "description": level.description, "level": level.level} for level in levels]

@router.get("/quizzes")
async def get_quizzes(db: AsyncSession = Depends(get_db)):
    """Get all quizzes with basic information"""
    result = await db.execute(select(Quiz))
    quizzes = result.scalars().all()
    return [{"id": quiz.id, "title": quiz.title, "status": quiz.status, "level_id": quiz.level_id} for quiz in quizzes]

@router.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific quiz including questions and answers"""
    result = await db.execute(select(Quiz).filter(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
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