"""
Refresh token model for JWT token management
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, UUID, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class RefreshToken(Base):
    """
    Refresh token model for managing JWT refresh tokens
    """
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    token = Column(String(500), nullable=False, unique=True, index=True)
    is_revoked = Column(Boolean, nullable=False, default=False)

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Device tracking (optional)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"

    def revoke(self):
        """Mark token as revoked"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)"""
        return not self.is_revoked and not self.is_expired()