"""
Shared test fixtures and configuration for Proyecto Semilla
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.core.config import settings
from backend.app.main import app


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def test_client(test_db) -> Generator[TestClient, None, None]:
    """Create test client with database session."""

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db):
    """Create a test user."""
    from backend.app.models.user import User
    from backend.app.models.tenant import Tenant
    from backend.app.models.role import Role
    from uuid import uuid4
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Create test tenant
    tenant = Tenant(
        id=uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        is_active=True
    )
    test_db.add(tenant)

    # Create test role
    role = Role(
        id=uuid4(),
        tenant_id=tenant.id,
        name="Admin",
        description="Administrator role",
        permissions=["*"],
        is_system=True
    )
    test_db.add(role)

    # Create test user
    user = User(
        id=uuid4(),
        tenant_id=tenant.id,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=pwd_context.hash("password123"),
        is_active=True,
        role_id=role.id
    )
    test_db.add(user)

    await test_db.commit()
    await test_db.refresh(user)

    return user


@pytest.fixture
async def auth_headers(test_client, test_user):
    """Create authentication headers for test user."""
    # Login to get access token
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Return empty headers if login fails
        return {}


@pytest.fixture
async def test_article(test_db, test_user):
    """Create a test article."""
    from backend.app.models.article import Article
    from uuid import uuid4

    article = Article(
        id=uuid4(),
        tenant_id=test_user.tenant_id,
        title="Test Article",
        slug="test-article",
        content="This is a test article content.",
        excerpt="Test excerpt",
        author_id=test_user.id,
        status="published",
        is_featured=False,
        view_count=0,
        comment_count=0,
        like_count=0,
        tags=["test", "article"]
    )

    test_db.add(article)
    await test_db.commit()
    await test_db.refresh(article)

    return article


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "security: Security tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )