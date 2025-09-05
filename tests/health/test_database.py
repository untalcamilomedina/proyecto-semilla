"""
Database Health Check Tests
Ensures database connectivity and performance
"""

import pytest
import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db


@pytest.mark.asyncio
async def test_database_connection():
    """Test basic database connectivity"""
    db = await get_db().__aenter__()
    try:
        result = await db.execute("SELECT 1 as test_value")
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1
    finally:
        await db.close()


@pytest.mark.asyncio
async def test_database_performance():
    """Test database query performance"""
    db = await get_db().__aenter__()
    try:
        # Test simple query performance
        start_time = time.time()
        result = await db.execute("SELECT COUNT(*) FROM users")
        count = result.fetchone()[0]
        query_time = time.time() - start_time

        # Should complete in less than 100ms
        assert query_time < 0.1, f"Query too slow: {query_time:.3f}s"
        assert isinstance(count, int)

    finally:
        await db.close()


@pytest.mark.asyncio
async def test_database_tables_exist():
    """Test that all required tables exist"""
    db = await get_db().__aenter__()
    try:
        required_tables = [
            'users', 'tenants', 'articles', 'categories',
            'refresh_tokens', 'user_roles', 'roles'
        ]

        for table in required_tables:
            result = await db.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}')")
            exists = result.fetchone()[0]
            assert exists, f"Table '{table}' does not exist"

    finally:
        await db.close()


@pytest.mark.asyncio
async def test_database_indexes():
    """Test that critical indexes exist"""
    db = await get_db().__aenter__()
    try:
        # Check for critical indexes
        critical_indexes = [
            'idx_articles_tenant_status',
            'idx_users_email',
            'idx_users_tenant_id'
        ]

        for index in critical_indexes:
            result = await db.execute(f"SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = '{index}')")
            exists = result.fetchone()[0]
            assert exists, f"Index '{index}' does not exist"

    finally:
        await db.close()


@pytest.mark.asyncio
async def test_row_level_security():
    """Test that RLS is enabled on critical tables"""
    db = await get_db().__aenter__()
    try:
        tables_with_rls = ['users', 'articles', 'categories']

        for table in tables_with_rls:
            result = await db.execute(f"SELECT row_security FROM information_schema.tables WHERE table_name = '{table}'")
            rls_enabled = result.fetchone()[0]
            assert rls_enabled, f"RLS not enabled on table '{table}'"

    finally:
        await db.close()