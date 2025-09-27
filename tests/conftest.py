"""Shared test fixtures and configuración para Proyecto Semilla."""

import asyncio
import sqlite3
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Asegura que el paquete `app` sea importable desde el repositorio raíz
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base, get_db  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
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


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
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

    role = Role(
        id=uuid4(),
        tenant_id=tenant.id,
        name="Admin",
        description="Admin",
        permissions='["*"]',
    )
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
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user."""
    token = create_access_token(subject=test_user.id, tenant_id=test_user.tenant_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_tenant_id(test_user: User) -> str:
    """Return the test user's tenant ID."""
    return str(test_user.tenant_id)


@pytest.fixture
@pytest.fixture
def test_user_id(test_user: User) -> str:
    """Return the test user's ID."""
    return str(test_user.id)


@pytest_asyncio.fixture
async def test_article(test_db: AsyncSession, test_user: User) -> Article:
    """Create a test article."""
    article = Article(
        tenant_id=test_user.tenant_id,
        author_id=test_user.id,
        title="Test Article",
        slug="test-article",
        content="<p>This is a test article content.</p>",
        excerpt="Test excerpt",
        status="published",
        tags=["test", "article"]
    )
    test_db.add(article)
    await test_db.commit()
    await test_db.refresh(article)
    return article


@pytest_asyncio.fixture
async def test_category(test_db: AsyncSession, test_user: User) -> Category:
    """Create a test category."""
    category = Category(
        tenant_id=test_user.tenant_id,
        name="Test Category",
        slug="test-category",
        description="Test category description"
    )
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    return category


@pytest_asyncio.fixture
async def test_comment(test_db: AsyncSession, test_user: User, test_article: Article) -> Comment:
    """Create a test comment."""
    comment = Comment(
        tenant_id=test_user.tenant_id,
        article_id=test_article.id,
        author_id=test_user.id,
        content="This is a test comment."
    )
    test_db.add(comment)
    await test_db.commit()
    await test_db.refresh(comment)
    return comment


@pytest_asyncio.fixture
async def test_role(test_db: AsyncSession, test_user: User) -> Role:
    """Create a test role."""
    role = Role(
        tenant_id=test_user.tenant_id,
        name="Editor",
        description="Content editor role",
        permissions='["read", "write", "edit"]'
    )
    test_db.add(role)
    await test_db.commit()
    await test_db.refresh(role)
    return role


@pytest_asyncio.fixture
async def test_tenant2(test_db: AsyncSession) -> Tenant:
    """Create a second test tenant for multi-tenant tests."""
    tenant = Tenant(name="Test Tenant 2", slug="test-tenant-2", is_active=True)
    test_db.add(tenant)
    await test_db.commit()
    await test_db.refresh(tenant)
    return tenant


@pytest_asyncio.fixture
async def test_user2(test_db: AsyncSession, test_tenant2: Tenant) -> User:
    """Create a user in the second tenant."""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        tenant_id=test_tenant2.id,
        email="user2@example.com",
        first_name="User",
        last_name="Two",
        full_name="User Two",
        hashed_password=pwd_context.hash("password123"),
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers2(test_user2: User) -> dict:
    """Create authentication headers for the second test user."""
    token = create_access_token(subject=test_user2.id, tenant_id=test_user2.tenant_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_tenant2_id(test_user2: User) -> str:
    """Return the second test user's tenant ID."""
    return str(test_user2.tenant_id)


@pytest.fixture
def test_user2_id(test_user2: User) -> str:
    """Return the second test user's ID."""
    return str(test_user2.id)
def test_user_id(test_user: User) -> str:
    """Return the test user's ID."""
    return str(test_user.id)
# Normaliza el manejo de UUID en SQLite para los tests
sqlite3.register_adapter(UUID, lambda value: str(value))
