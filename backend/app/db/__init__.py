# DB package for database setup and session management

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Base
from sqlalchemy import event

# NOTE: DATABASE_URL must use an async driver, e.g., 'sqlite+aiosqlite:///...'
engine = create_async_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite specific - needed for FastAPI
)

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create session factory for async sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create all tables in the database (async, to be awaited from FastAPI startup)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Async dependency for getting a database session"""
    async with SessionLocal() as session:
        yield session
