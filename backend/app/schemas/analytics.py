"""
Pydantic schemas for Analytics API
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyticsEventCreate(BaseModel):
    """Schema for creating analytics events"""
    event_type: str = Field(..., description="Type of event (page_view, user_action, api_call, error)")
    event_name: str = Field(..., description="Specific event name")
    session_id: Optional[str] = Field(None, description="User session ID")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event properties")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class AnalyticsEventResponse(BaseModel):
    """Schema for analytics event responses"""
    id: UUID
    tenant_id: UUID
    event_type: str
    event_name: str
    user_id: Optional[UUID]
    session_id: Optional[str]
    properties: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsResponse(BaseModel):
    """Schema for metrics data responses"""
    tenant_id: UUID
    time_bucket: str
    days: int
    metrics: Dict[str, List[Dict[str, Any]]] = Field(..., description="Metrics data by name")


class RealtimeMetricsResponse(BaseModel):
    """Schema for real-time metrics responses"""
    tenant_id: UUID
    hours: int
    active_users_24h: int
    events_last_24h: int
    errors_last_24h: int
    timestamp: str


class DashboardCreate(BaseModel):
    """Schema for creating dashboards"""
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    config: Dict[str, Any] = Field(default_factory=dict, description="Dashboard configuration")
    is_public: str = Field("private", description="Visibility: private, tenant, public")


class DashboardUpdate(BaseModel):
    """Schema for updating dashboards"""
    name: Optional[str] = Field(None, description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    config: Optional[Dict[str, Any]] = Field(None, description="Dashboard configuration")
    is_public: Optional[str] = Field(None, description="Visibility: private, tenant, public")


class DashboardResponse(BaseModel):
    """Schema for dashboard responses"""
    id: UUID
    tenant_id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    config: Dict[str, Any]
    is_public: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    """Schema for creating reports"""
    name: str = Field(..., description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    report_type: str = Field(..., description="Report type: daily, weekly, monthly, custom")
    schedule_config: Dict[str, Any] = Field(..., description="Schedule configuration")
    recipients: Optional[List[str]] = Field(None, description="Email recipients")
    config: Dict[str, Any] = Field(..., description="Report configuration")


class ReportResponse(BaseModel):
    """Schema for report responses"""
    id: UUID
    tenant_id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    report_type: str
    schedule_config: Dict[str, Any]
    is_active: str
    recipients: Optional[List[str]]
    config: Dict[str, Any]
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummaryResponse(BaseModel):
    """Schema for analytics summary responses"""
    tenant_id: UUID
    period_days: int
    summary: Dict[str, Dict[str, Any]] = Field(..., description="Summary data by metric")


class MetricDataPoint(BaseModel):
    """Schema for individual metric data points"""
    date: str
    value: float
    bucket_start: str
    bucket_end: str


class MetricSeries(BaseModel):
    """Schema for metric time series"""
    name: str
    data: List[MetricDataPoint]
    total: float
    average: float
    trend: str  # 'up', 'down', 'stable', 'no_data'