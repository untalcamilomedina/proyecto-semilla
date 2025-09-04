"""
Database configuration and connection management
SQLAlchemy setup with PostgreSQL and async support
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
    poolclass=StaticPool,
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables
    """
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import Tenant, User, Role, UserRole  # noqa

        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Drop all database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def reset_database():
    """
    Reset database by dropping and recreating all tables
    """
    await drop_tables()
    await create_tables()