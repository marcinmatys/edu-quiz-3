import pytest
import asyncio
from typing import Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import FastAPI

from ..models.base import Base
from ..db import get_db
from ..main import app
from ..core.config import settings

# Create test database engine
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    class_=AsyncSession, 
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_db():
    """Setup the test database once for all tests"""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(setup_db) -> AsyncSession:
    """Get a database session for each test"""
    async with TestingSessionLocal() as session:
        # Start a nested transaction
        transaction = await session.begin_nested()
        
        yield session
        
        # Rollback the nested transaction
        await transaction.rollback()

@pytest.fixture
async def client(db_session) -> Generator:
    """Get a test client with overridden dependencies"""
    # Override the get_db dependency
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Remove the override after test
    app.dependency_overrides.clear()

@pytest.fixture
def test_app() -> FastAPI:
    """Get the FastAPI app instance for testing"""
    return app 