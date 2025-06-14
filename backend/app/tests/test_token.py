import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest_asyncio

from app.main import app
from app.db import get_db, Base
from app.models.user import User
from app.core.security import get_password_hash

# Create test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

# Override the get_db dependency
async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture()
async def test_db():
    # Create the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a test user
    async with TestingSessionLocal() as db:
        test_user = User(
            username="testuser",
            hashed_password=get_password_hash("testpassword"),
            role="student"
        )
        db.add(test_user)
        await db.commit()
    
    yield
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_login_success(test_db):
    """Test successful login with correct credentials"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "testpassword"}
        )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert len(token_data["access_token"]) > 0

@pytest.mark.asyncio
async def test_login_wrong_password(test_db):
    """Test login with wrong password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Incorrect username or password"}

@pytest.mark.asyncio
async def test_login_wrong_username(test_db):
    """Test login with non-existent username"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent", "password": "testpassword"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Incorrect username or password"} 