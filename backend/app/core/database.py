"""
Database configuration and connection management
SQLAlchemy setup with PostgreSQL and async support
"""

import contextvars
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import Request

from app.core.config import settings

# Context variable to store tenant_id across async calls
tenant_context: contextvars.ContextVar[str] = contextvars.ContextVar('tenant_id', default=None)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
    # Removed StaticPool - using default AsyncAdaptedQueuePool for better async support
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,  # Prevent automatic flushing that can cause context issues
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    Improved async context management to prevent greenlet issues
    Sets tenant context for RLS if tenant_id is available in context
    """
    session = async_session()
    try:
        # Set tenant context for RLS if available
        tenant_id = tenant_context.get()
        if tenant_id:
            await session.execute(text("SET LOCAL app.current_tenant_id = :tenant_id"), {"tenant_id": tenant_id})

        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def set_tenant_context(tenant_id: str):
    """
    Set tenant context for the current async context
    """
    tenant_context.set(tenant_id)


async def create_tables():
    """
    Create all database tables
    """
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import Tenant, User, Role, UserRole, RefreshToken  # noqa

        # await conn.run_sync(Base.metadata.create_all)


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


async def create_rls_functions():
    """
    Create PostgreSQL functions required for Row Level Security
    """
    async with engine.begin() as conn:
        # Create function to get current tenant_id from session
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION current_tenant_id()
            RETURNS UUID AS $$
            BEGIN
                RETURN current_setting('app.current_tenant_id')::UUID;
            EXCEPTION
                WHEN undefined_object THEN
                    RAISE EXCEPTION 'Tenant context not set. Use SET LOCAL app.current_tenant_id = ''your-tenant-id'';';
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;
        """))

        # Create function to check if user belongs to current tenant
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION user_belongs_to_current_tenant(user_tenant_id UUID)
            RETURNS BOOLEAN AS $$
            BEGIN
                RETURN user_tenant_id = current_tenant_id();
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;
        """))


async def set_tenant_context(session: AsyncSession, tenant_id: str):
    """
    Set tenant context for the current database session
    """
    await session.execute(text("SET LOCAL app.current_tenant_id = :tenant_id"), {"tenant_id": tenant_id})