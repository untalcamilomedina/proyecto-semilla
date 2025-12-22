"""
Pytest fixtures for Proyecto Semilla.

Provides reusable fixtures for:
- Database setup with tenant schemas
- User and membership creation
- API client authentication
- Common test data factories
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

if TYPE_CHECKING:
    from core.models import Membership, Role
    from multitenant.models import Tenant

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user(db) -> User:
    """Create and return a basic test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db) -> User:
    """Create and return a superuser."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def tenant(db) -> "Tenant":
    """Create and return a test tenant."""
    from multitenant.models import Tenant

    tenant = Tenant.objects.create(
        name="Test Organization",
        slug="test-org",
        schema_name="test_org",
    )
    # Create schema if using schema-based multitenancy
    try:
        tenant.create_schema(check_if_exists=True)
    except Exception:
        pass  # Schema might already exist or not be needed
    return tenant


@pytest.fixture
def owner_role(db, tenant: "Tenant") -> "Role":
    """Create and return the owner role for the tenant."""
    from core.models import Role

    role, _ = Role.objects.get_or_create(
        organization=tenant,
        slug="owner",
        defaults={
            "name": "Owner",
            "description": "Full access to organization",
            "is_system": True,
            "position": 100,
        },
    )
    return role


@pytest.fixture
def member_role(db, tenant: "Tenant") -> "Role":
    """Create and return the member role for the tenant."""
    from core.models import Role

    role, _ = Role.objects.get_or_create(
        organization=tenant,
        slug="member",
        defaults={
            "name": "Member",
            "description": "Standard member access",
            "is_system": True,
            "position": 10,
        },
    )
    return role


@pytest.fixture
def owner_membership(db, user: User, tenant: "Tenant", owner_role: "Role") -> "Membership":
    """Create and return an owner membership for the test user."""
    from core.models import Membership

    membership, _ = Membership.objects.get_or_create(
        user=user,
        organization=tenant,
        defaults={"role": owner_role, "is_active": True},
    )
    return membership


@pytest.fixture
def member_membership(db, tenant: "Tenant", member_role: "Role") -> "Membership":
    """Create a member user with membership."""
    from core.models import Membership

    member_user = User.objects.create_user(
        username="member",
        email="member@example.com",
        password="memberpass123",
    )
    membership = Membership.objects.create(
        user=member_user,
        organization=tenant,
        role=member_role,
        is_active=True,
    )
    return membership


@pytest.fixture
def authenticated_client(api_client: APIClient, user: User) -> APIClient:
    """Return an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def tenant_client(
    api_client: APIClient,
    user: User,
    tenant: "Tenant",
    owner_membership: "Membership",
) -> APIClient:
    """Return an authenticated API client with tenant context.

    This fixture sets up:
    - Authenticated user
    - User has owner membership in tenant
    - Request includes tenant header (if needed)
    """
    api_client.force_authenticate(user=user)
    # Add tenant header for API requests
    api_client.defaults["HTTP_X_TENANT"] = tenant.slug
    return api_client


@pytest.fixture
def sample_permissions(db):
    """Create a set of sample permissions for testing."""
    from core.models import Permission

    permissions = []
    permission_data = [
        ("core", "manage_roles", "Manage Roles"),
        ("core", "invite_members", "Invite Members"),
        ("core", "view_members", "View Members"),
        ("billing", "manage_billing", "Manage Billing"),
        ("billing", "view_invoices", "View Invoices"),
    ]

    for module, codename, name in permission_data:
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={"module": module, "name": name, "is_system": True},
        )
        permissions.append(perm)

    return permissions
