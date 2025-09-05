"""
Real-Time Analytics Models for Proyecto Semilla
Advanced analytics with ML predictions and automated insights
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class EventType(Enum):
    """Types of analytics events"""
    PAGE_VIEW = "page_view"
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    ERROR = "error"
    PERFORMANCE = "performance"
    CONVERSION = "conversion"
    COLLABORATION = "collaboration"
    CUSTOM = "custom"

class MetricType(Enum):
    """Types of metrics"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"

class PredictionModel(Enum):
    """ML prediction models"""
    LINEAR_REGRESSION = "linear_regression"
    TIME_SERIES = "time_series"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    CLASSIFICATION = "classification"

@dataclass
class AnalyticsEvent:
    """Real-time analytics event"""
    id: str
    event_type: EventType
    user_id: Optional[str]
    session_id: str
    tenant_id: Optional[str]
    timestamp: datetime
    properties: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MetricData:
    """Metric data point"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str]
    metric_type: MetricType = MetricType.COUNT

@dataclass
class PredictionResult:
    """ML prediction result"""
    model_id: str
    prediction: Any
    confidence: float
    features: Dict[str, Any]
    timestamp: datetime
    model_type: PredictionModel

@dataclass
class Insight:
    """Automated insight"""
    id: str
    title: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str
    data: Dict[str, Any]
    timestamp: datetime
    confidence: float
    actions: List[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.actions is None:
            self.actions = []

@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    id: str
    title: str
    type: str  # 'chart', 'metric', 'table', 'map'
    data_source: str
    config: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height
    refresh_interval: int = 30  # seconds

@dataclass
class ABTest:
    """A/B testing configuration"""
    id: str
    name: str
    description: str
    variants: List[Dict[str, Any]]
    target_metric: str
    start_date: datetime
    end_date: Optional[datetime]
    status: str = "draft"  # 'draft', 'running', 'completed', 'stopped'
    winner: Optional[str] = None

# SQLAlchemy Models

class AnalyticsEventModel(Base):
    """Database model for analytics events"""
    __tablename__ = "analytics_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False)
    user_id = Column(String(36), index=True)
    session_id = Column(String(36), index=True)
    tenant_id = Column(String(36), index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    properties = Column(JSON, nullable=False)
    metadata = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

class MetricModel(Base):
    """Database model for metrics"""
    __tablename__ = "analytics_metrics"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    tags = Column(JSON)
    metric_type = Column(String(20), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class PredictionModelModel(Base):
    """Database model for ML prediction models"""
    __tablename__ = "analytics_prediction_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    accuracy_score = Column(Float)
    last_trained = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InsightModel(Base):
    """Database model for automated insights"""
    __tablename__ = "analytics_insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    actions = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

class DashboardModel(Base):
    """Database model for dashboards"""
    __tablename__ = "analytics_dashboards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tenant_id = Column(String(36), index=True)
    user_id = Column(String(36), index=True)
    config = Column(JSON, nullable=False)
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ABTestModel(Base):
    """Database model for A/B tests"""
    __tablename__ = "analytics_ab_tests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    variants = Column(JSON, nullable=False)
    target_metric = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20), nullable=False, default="draft")
    winner = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSegmentModel(Base):
    """Database model for user segments"""
    __tablename__ = "analytics_user_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tenant_id = Column(String(36), index=True)
    criteria = Column(JSON, nullable=False)
    user_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Utility functions

def create_event(event_type: EventType, user_id: Optional[str], session_id: str,
                tenant_id: Optional[str], properties: Dict[str, Any],
                metadata: Optional[Dict[str, Any]] = None) -> AnalyticsEvent:
    """Create a new analytics event"""
    return AnalyticsEvent(
        id=str(uuid.uuid4()),
        event_type=event_type,
        user_id=user_id,
        session_id=session_id,
        tenant_id=tenant_id,
        timestamp=datetime.utcnow(),
        properties=properties,
        metadata=metadata or {}
    )

def create_metric(name: str, value: Union[int, float], tags: Dict[str, str],
                 metric_type: MetricType = MetricType.COUNT) -> MetricData:
    """Create a new metric data point"""
    return MetricData(
        name=name,
        value=value,
        timestamp=datetime.utcnow(),
        tags=tags,
        metric_type=metric_type
    )

def create_insight(title: str, description: str, severity: str, category: str,
                  data: Dict[str, Any], confidence: float,
                  actions: Optional[List[Dict[str, Any]]] = None) -> Insight:
    """Create a new automated insight"""
    return Insight(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        severity=severity,
        category=category,
        data=data,
        timestamp=datetime.utcnow(),
        confidence=confidence,
        actions=actions or []
    )

# Analytics configuration
ANALYTICS_CONFIG = {
    "retention_days": 90,
    "batch_size": 1000,
    "real_time_window": 300,  # 5 minutes
    "prediction_interval": 3600,  # 1 hour
    "insight_threshold": 0.8,  # 80% confidence
    "max_concurrent_predictions": 10
}