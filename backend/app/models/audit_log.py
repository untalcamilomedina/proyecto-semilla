"""
Audit Log model for comprehensive audit trail
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, UUID, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """
    Audit Log model for tracking all system activities
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Event information
    event_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'

    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    # User context
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    session_id = Column(String(36), nullable=True)

    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Resource information
    resource = Column(String(500), nullable=True)
    action = Column(String(50), nullable=True)

    # Result
    status = Column(String(20), nullable=False)  # 'success', 'failure', 'error', 'warning'

    # Additional information
    description = Column(Text, nullable=True)
    event_metadata = Column(JSONB, nullable=True)
    tags = Column(JSONB, nullable=True)

    # Integrity
    hash = Column(String(64), nullable=False)  # SHA-256 hash for integrity

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', tenant_id={self.tenant_id})>"