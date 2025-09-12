"""
Shared test fixtures and configuration for Proyecto Semilla
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.models.user import User


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncSession, None]:
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for a test."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    
    async_session_maker = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )
    
    session = async_session_maker()
    
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    from app.models.tenant import Tenant
    from app.models.role import Role
    from app.models.user_role import UserRole
    from uuid import uuid4
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    tenant = Tenant(id=uuid4(), name="Test Tenant", slug="test-tenant", is_active=True)
    test_db.add(tenant)

    role = Role(id=uuid4(), tenant_id=tenant.id, name="Admin", description="Admin", permissions=["*"])
    test_db.add(role)

    user = User(
        id=uuid4(),
        tenant_id=tenant.id,
        email=settings.TEST_USER_EMAIL,
        first_name="Test",
        last_name="User",
        full_name="Test User",
        hashed_password=pwd_context.hash(settings.TEST_USER_PASSWORD),
        is_active=True,
    )
    test_db.add(user)

    user_role = UserRole(user_id=user.id, role_id=role.id)
    test_db.add(user_role)

    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Create authentication headers for test user."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": settings.TEST_USER_PASSWORD},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_tenant_id(test_user: User) -> str:
    """Return the test user's tenant ID."""
    return str(test_user.tenant_id)


@pytest.fixture
def test_user_id(test_user: User) -> str:
    """Return the test user's ID."""
    return str(test_user.id)