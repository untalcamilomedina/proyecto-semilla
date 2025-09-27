"""
System User Flag Model
Model for marking users as system users instead of using hardcoded emails
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class SystemUserFlag(Base):
    """
    System User Flag Model - Security Enhancement

    SECURITY PURPOSE:
    This model replaces insecure hardcoded email lists with a database-driven
    approach to identify system users. This eliminates critical security
    vulnerabilities present in the previous hardcoded system.

    PREVIOUS VULNERABILITIES ADDRESSED:
    - Hardcoded credentials exposed in source code
    - No separation between system and regular users
    - Difficult to audit system user creation/modification
    - Inflexible user management for different environments

    NEW SECURITY FEATURES:
    - Database-driven user classification
    - Configurable system users via environment variables
    - Clear audit trail of system user creation
    - Support for multiple system user types
    - Migration path from legacy hardcoded users

    FLAG TYPES:
    - 'admin': System administrator with full access
    - 'demo': Demo user for testing/showcase purposes
    - 'system': Generic system user
    - 'legacy_hardcoded': Users migrated from old hardcoded system

    DATABASE INTEGRITY:
    - Foreign key constraint ensures user exists
    - Composite primary key prevents duplicate flags
    - Automatic timestamps for audit trail
    - Cascade delete maintains referential integrity

    MIGRATION CONSIDERATIONS:
    - Existing hardcoded users are automatically flagged during migration
    - Backward compatibility maintained during transition period
    - Feature flag controls migration activation
    """
    __tablename__ = "system_user_flags"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    flag_type = Column(String(50), primary_key=True)  # 'admin', 'demo', 'system', 'legacy_hardcoded'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemUserFlag(user_id={self.user_id}, flag_type={self.flag_type})>"