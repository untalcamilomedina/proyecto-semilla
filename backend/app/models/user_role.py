"""
User-Role association model for many-to-many relationship
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(Base):
    """
    Association table for User-Role many-to-many relationship
    """
    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"