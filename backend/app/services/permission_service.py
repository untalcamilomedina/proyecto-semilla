"""
Permission validation service for role-based access control
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.models.user import User
from app.models.role import Role


class PermissionService:
    """
    Service for handling permission validation and role-based access control
    """

    @staticmethod
    async def get_user_permissions(user_id: UUID, tenant_id: UUID, db: AsyncSession) -> List[str]:
        """
        Get all permissions for a user across all their roles
        """
        result = await db.execute(
            text("""
                SELECT DISTINCT jsonb_array_elements_text(r.permissions::jsonb) as permission
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
                WHERE u.id = :user_id AND u.tenant_id = :tenant_id AND r.is_active = true
            """),
            {"user_id": user_id, "tenant_id": tenant_id}
        )

        permissions = result.fetchall()
        return [row[0] for row in permissions]

    @staticmethod
    async def has_permission(user_id: UUID, tenant_id: UUID, permission: str, db: AsyncSession) -> bool:
        """
        Check if user has a specific permission
        """
        permissions = await PermissionService.get_user_permissions(user_id, tenant_id, db)
        return permission in permissions

    @staticmethod
    async def has_any_permission(user_id: UUID, tenant_id: UUID, permissions: List[str], db: AsyncSession) -> bool:
        """
        Check if user has any of the specified permissions
        """
        user_permissions = await PermissionService.get_user_permissions(user_id, tenant_id, db)
        return any(perm in user_permissions for perm in permissions)

    @staticmethod
    async def has_all_permissions(user_id: UUID, tenant_id: UUID, permissions: List[str], db: AsyncSession) -> bool:
        """
        Check if user has all of the specified permissions
        """
        user_permissions = await PermissionService.get_user_permissions(user_id, tenant_id, db)
        return all(perm in user_permissions for perm in permissions)

    @staticmethod
    async def get_user_roles(user_id: UUID, tenant_id: UUID, db: AsyncSession) -> List[Role]:
        """
        Get all roles for a user
        """
        result = await db.execute(
            text("""
                SELECT r.* FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                JOIN users u ON ur.user_id = u.id
                WHERE u.id = :user_id AND u.tenant_id = :tenant_id AND r.is_active = true
                ORDER BY r.hierarchy_level DESC
            """),
            {"user_id": user_id, "tenant_id": tenant_id}
        )

        roles_data = result.fetchall()

        # Convert to Role objects
        roles = []
        for row in roles_data:
            import json
            try:
                permissions = json.loads(row[4]) if row[4] else []
            except (json.JSONDecodeError, TypeError):
                permissions = []

            role = Role(
                id=row[0],
                tenant_id=row[1],
                name=row[2],
                description=row[3],
                permissions=json.dumps(permissions),
                color=row[5],
                hierarchy_level=row[6],
                is_default=row[7],
                is_active=row[8],
                created_at=row[9],
                updated_at=row[10]
            )
            roles.append(role)

        return roles

    @staticmethod
    async def get_highest_role_level(user_id: UUID, tenant_id: UUID, db: AsyncSession) -> int:
        """
        Get the highest hierarchy level among user's roles
        """
        result = await db.execute(
            text("""
                SELECT MAX(r.hierarchy_level) as max_level
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                JOIN users u ON ur.user_id = u.id
                WHERE u.id = :user_id AND u.tenant_id = :tenant_id AND r.is_active = true
            """),
            {"user_id": user_id, "tenant_id": tenant_id}
        )

        row = result.fetchone()
        return row[0] if row and row[0] is not None else 0

    @staticmethod
    async def can_manage_role(user_id: UUID, tenant_id: UUID, target_role_id: UUID, db: AsyncSession) -> bool:
        """
        Check if user can manage (assign/remove) a specific role
        """
        # Get user's highest role level
        user_level = await PermissionService.get_highest_role_level(user_id, tenant_id, db)

        # Get target role level
        result = await db.execute(
            text("SELECT hierarchy_level FROM roles WHERE id = :role_id AND tenant_id = :tenant_id"),
            {"role_id": target_role_id, "tenant_id": tenant_id}
        )

        row = result.fetchone()
        if not row:
            return False

        target_level = row[0]

        # User can manage roles with lower or equal hierarchy level
        return user_level > target_level

    @staticmethod
    async def validate_permission_access(user_id: UUID, tenant_id: UUID, required_permissions: List[str], db: AsyncSession, require_all: bool = False) -> bool:
        """
        Validate if user has required permissions for an action

        Args:
            user_id: User ID
            tenant_id: Tenant ID
            required_permissions: List of required permissions
            db: Database session
            require_all: If True, user must have ALL permissions; if False, user must have ANY

        Returns:
            True if user has required permissions, False otherwise
        """
        if not required_permissions:
            return True

        if require_all:
            return await PermissionService.has_all_permissions(user_id, tenant_id, required_permissions, db)
        else:
            return await PermissionService.has_any_permission(user_id, tenant_id, required_permissions, db)


# Permission constants for easy reference
class Permissions:
    """Permission constants"""

    # User permissions
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"

    # Tenant permissions
    TENANTS_READ = "tenants:read"
    TENANTS_WRITE = "tenants:write"
    TENANTS_DELETE = "tenants:delete"

    # Article permissions
    ARTICLES_READ = "articles:read"
    ARTICLES_WRITE = "articles:write"
    ARTICLES_DELETE = "articles:delete"
    ARTICLES_PUBLISH = "articles:publish"

    # Role permissions
    ROLES_READ = "roles:read"
    ROLES_WRITE = "roles:write"
    ROLES_DELETE = "roles:delete"

    # Category permissions
    CATEGORIES_READ = "categories:read"
    CATEGORIES_WRITE = "categories:write"
    CATEGORIES_DELETE = "categories:delete"

    # Comment permissions
    COMMENTS_READ = "comments:read"
    COMMENTS_WRITE = "comments:write"
    COMMENTS_DELETE = "comments:delete"

    # System permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"

    @classmethod
    def get_all_permissions(cls) -> List[str]:
        """Get all available permissions"""
        return [
            cls.USERS_READ, cls.USERS_WRITE, cls.USERS_DELETE,
            cls.TENANTS_READ, cls.TENANTS_WRITE, cls.TENANTS_DELETE,
            cls.ARTICLES_READ, cls.ARTICLES_WRITE, cls.ARTICLES_DELETE, cls.ARTICLES_PUBLISH,
            cls.ROLES_READ, cls.ROLES_WRITE, cls.ROLES_DELETE,
            cls.CATEGORIES_READ, cls.CATEGORIES_WRITE, cls.CATEGORIES_DELETE,
            cls.COMMENTS_READ, cls.COMMENTS_WRITE, cls.COMMENTS_DELETE,
            cls.SYSTEM_ADMIN, cls.SYSTEM_CONFIG
        ]