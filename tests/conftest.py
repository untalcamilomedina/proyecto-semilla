"""
Pytest configuration and global fixtures for Proyecto Semilla
"""

import asyncio
from typing import Dict

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def client():
    """Create test HTTP client."""
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.fixture
def auth_headers(client: AsyncClient):
    """Get authentication headers for test user."""
    async def _get_headers():
        login_data = {
            "username": "admin@proyecto-semilla.com",
            "password": "admin123"
        }

        response = await client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200

        token_data = response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}

    import asyncio
    return asyncio.run(_get_headers())