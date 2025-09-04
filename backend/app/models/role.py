"""
Role model for role-based access control (RBAC)
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    """
    Role model representing user roles with permissions
    """
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Visual properties for UI
    color = Column(String(7), nullable=False, default="#ffffff")  # Hex color

    # Permissions as JSON array of strings
    permissions = Column(Text, nullable=False, default="[]")  # JSON array

    # Hierarchy and status
    hierarchy_level = Column(Integer, nullable=False, default=0)
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"

    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission"""
        import json
        try:
            perms = json.loads(self.permissions)
            return permission in perms
        except (json.JSONDecodeError, TypeError):
            return False

    def add_permission(self, permission: str):
        """Add a permission to the role"""
        import json
        try:
            perms = json.loads(self.permissions)
        except (json.JSONDecodeError, TypeError):
            perms = []

        if permission not in perms:
            perms.append(permission)
            self.permissions = json.dumps(perms)

    def remove_permission(self, permission: str):
        """Remove a permission from the role"""
        import json
        try:
            perms = json.loads(self.permissions)
        except (json.JSONDecodeError, TypeError):
            perms = []

        if permission in perms:
            perms.remove(permission)
            self.permissions = json.dumps(perms)