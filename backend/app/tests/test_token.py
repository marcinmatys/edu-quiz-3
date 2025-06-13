import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db, Base
from app.models.user import User
from app.core.security import get_password_hash

# Create test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test user
    db = TestingSessionLocal()
    test_user = User(
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        role="student"
    )
    db.add(test_user)
    db.commit()
    
    yield db
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

def test_login_success(test_db):
    """Test successful login with correct credentials"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert len(token_data["access_token"]) > 0

def test_login_wrong_password(test_db):
    """Test login with wrong password"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_wrong_username(test_db):
    """Test login with non-existent username"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nonexistent", "password": "testpassword"}
    )
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"} 