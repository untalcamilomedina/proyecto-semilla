"""
Basic Analytics models for Proyecto Semilla
Simple analytics system with multi-tenant support and RLS compatibility
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, Integer, Float, UUID, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalyticsEvent(Base):
    """
    Basic analytics event model for tracking user actions and system events
    """
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Event information
    event_type = Column(String(50), nullable=False, index=True)  # 'page_view', 'user_action', 'api_call', 'error'
    event_name = Column(String(100), nullable=False, index=True)

    # User context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(36), nullable=True, index=True)

    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Event data
    properties = Column(JSONB, nullable=True)  # Additional event properties
    event_metadata = Column(JSONB, nullable=True)   # System metadata

    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", backref="analytics_events")
    user = relationship("User", backref="analytics_events")

    # Indexes for performance
    __table_args__ = (
        Index('idx_analytics_events_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('idx_analytics_events_tenant_type', 'tenant_id', 'event_type'),
        Index('idx_analytics_events_user_timestamp', 'user_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, event_type='{self.event_type}', tenant_id={self.tenant_id})>"


class AnalyticsMetric(Base):
    """
    Basic metrics model for storing aggregated analytics data
    """
    __tablename__ = "analytics_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Metric information
    metric_name = Column(String(100), nullable=False, index=True)  # 'active_users', 'articles_published', 'api_requests'
    metric_value = Column(Float, nullable=False)

    # Time aggregation
    time_bucket = Column(String(20), nullable=False, index=True)  # 'hour', 'day', 'week', 'month'
    bucket_start = Column(DateTime(timezone=True), nullable=False, index=True)
    bucket_end = Column(DateTime(timezone=True), nullable=False, index=True)

    # Dimensions
    dimensions = Column(JSONB, nullable=True)  # Additional grouping dimensions

    # Metadata
    source = Column(String(50), nullable=True)  # 'automatic', 'manual', 'api'
    tags = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", backref="analytics_metrics")

    # Indexes for performance
    __table_args__ = (
        Index('idx_analytics_metrics_tenant_name_time', 'tenant_id', 'metric_name', 'time_bucket', 'bucket_start'),
        Index('idx_analytics_metrics_tenant_bucket', 'tenant_id', 'bucket_start', 'bucket_end'),
    )

    def __repr__(self):
        return f"<AnalyticsMetric(id={self.id}, name='{self.metric_name}', value={self.metric_value}, tenant_id={self.tenant_id})>"


class AnalyticsDashboard(Base):
    """
    Dashboard configuration for storing user-defined analytics views
    """
    __tablename__ = "analytics_dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Dashboard information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Configuration
    config = Column(JSONB, nullable=False)  # Dashboard layout and widget configuration
    is_public = Column(String(10), nullable=False, default='private')  # 'private', 'tenant', 'public'

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", backref="analytics_dashboards")
    user = relationship("User", backref="analytics_dashboards")

    # Indexes for performance
    __table_args__ = (
        Index('idx_analytics_dashboards_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_analytics_dashboards_tenant_public', 'tenant_id', 'is_public'),
    )

    def __repr__(self):
        return f"<AnalyticsDashboard(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"


class AnalyticsReport(Base):
    """
    Scheduled reports model for automated report generation
    """
    __tablename__ = "analytics_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Report information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly', 'custom'

    # Schedule configuration
    schedule_config = Column(JSONB, nullable=False)  # Cron expression or schedule details
    is_active = Column(String(10), nullable=False, default='active')  # 'active', 'paused', 'inactive'

    # Recipients
    recipients = Column(JSONB, nullable=True)  # List of email addresses or user IDs

    # Report configuration
    config = Column(JSONB, nullable=False)  # Report structure and metrics to include

    # Last execution
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", backref="analytics_reports")
    user = relationship("User", backref="analytics_reports")

    # Indexes for performance
    __table_args__ = (
        Index('idx_analytics_reports_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_analytics_reports_next_run', 'next_run_at'),
        Index('idx_analytics_reports_active', 'is_active'),
    )

    def __repr__(self):
        return f"<AnalyticsReport(id={self.id}, name='{self.name}', type='{self.report_type}', tenant_id={self.tenant_id})>"