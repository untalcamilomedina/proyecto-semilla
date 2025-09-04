"""
Tests for health check endpoint
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint returns correct response"""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_check_content_type(client: AsyncClient):
    """Test health check returns correct content type"""
    response = await client.get("/health")

    assert response.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_health_check_method_not_allowed(client: AsyncClient):
    """Test health check rejects invalid HTTP methods"""
    response = await client.post("/health")

    assert response.status_code == 405  # Method Not Allowed