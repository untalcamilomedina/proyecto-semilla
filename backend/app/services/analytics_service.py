"""
Basic Analytics Service for Proyecto Semilla
Handles automatic metric collection, aggregation, and analytics operations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
import logging

from sqlalchemy import func, and_, or_, desc, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.analytics import AnalyticsEvent, AnalyticsMetric, AnalyticsDashboard, AnalyticsReport
from app.models.user import User
from app.models.audit_log import AuditLog
from app.core.database import get_db

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics operations and metric collection"""

    def __init__(self, db: Session):
        self.db = db

    def track_event(self, tenant_id: UUID, event_type: str, event_name: str,
                   user_id: Optional[UUID] = None, session_id: Optional[str] = None,
                   properties: Optional[Dict[str, Any]] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> AnalyticsEvent:
        """
        Track an analytics event
        """
        try:
            event = AnalyticsEvent(
                tenant_id=tenant_id,
                event_type=event_type,
                event_name=event_name,
                user_id=user_id,
                session_id=session_id,
                properties=properties or {},
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata or {},
                timestamp=datetime.utcnow()
            )

            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)

            logger.info(f"Tracked event: {event_type}.{event_name} for tenant {tenant_id}")
            return event

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error tracking event: {e}")
            raise

    def collect_daily_metrics(self, tenant_id: UUID, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Collect daily metrics for a tenant
        """
        if date is None:
            date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        next_date = date + timedelta(days=1)

        try:
            # Active users (users who logged in or performed actions)
            active_users = self.db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
                and_(
                    AnalyticsEvent.tenant_id == tenant_id,
                    AnalyticsEvent.timestamp >= date,
                    AnalyticsEvent.timestamp < next_date,
                    AnalyticsEvent.user_id.isnot(None)
                )
            ).scalar() or 0

            # Articles published (commented out - CMS removed)
            # articles_published = self.db.query(func.count(Article.id)).filter(
            #     and_(
            #         Article.tenant_id == tenant_id,
            #         Article.status == 'published',
            #         Article.published_at >= date,
            #         Article.published_at < next_date
            #     )
            # ).scalar() or 0
            articles_published = 0

            # API requests (from audit logs)
            api_requests = self.db.query(func.count(AuditLog.id)).filter(
                and_(
                    AuditLog.tenant_id == tenant_id,
                    AuditLog.event_type == 'api_call',
                    AuditLog.timestamp >= date,
                    AuditLog.timestamp < next_date
                )
            ).scalar() or 0

            # Errors
            errors = self.db.query(func.count(AnalyticsEvent.id)).filter(
                and_(
                    AnalyticsEvent.tenant_id == tenant_id,
                    AnalyticsEvent.event_type == 'error',
                    AnalyticsEvent.timestamp >= date,
                    AnalyticsEvent.timestamp < next_date
                )
            ).scalar() or 0

            # Page views
            page_views = self.db.query(func.count(AnalyticsEvent.id)).filter(
                and_(
                    AnalyticsEvent.tenant_id == tenant_id,
                    AnalyticsEvent.event_type == 'page_view',
                    AnalyticsEvent.timestamp >= date,
                    AnalyticsEvent.timestamp < next_date
                )
            ).scalar() or 0

            metrics = {
                'active_users': active_users,
                'articles_published': articles_published,
                'api_requests': api_requests,
                'errors': errors,
                'page_views': page_views
            }

            # Store metrics
            for metric_name, value in metrics.items():
                self._store_metric(
                    tenant_id=tenant_id,
                    metric_name=metric_name,
                    value=value,
                    time_bucket='day',
                    bucket_start=date,
                    bucket_end=next_date,
                    source='automatic'
                )

            logger.info(f"Collected daily metrics for tenant {tenant_id}: {metrics}")
            return metrics

        except SQLAlchemyError as e:
            logger.error(f"Error collecting daily metrics: {e}")
            raise

    def _store_metric(self, tenant_id: UUID, metric_name: str, value: float,
                     time_bucket: str, bucket_start: datetime, bucket_end: datetime,
                     dimensions: Optional[Dict[str, Any]] = None, source: str = 'automatic') -> AnalyticsMetric:
        """
        Store a metric value
        """
        try:
            # Check if metric already exists for this time bucket
            existing_metric = self.db.query(AnalyticsMetric).filter(
                and_(
                    AnalyticsMetric.tenant_id == tenant_id,
                    AnalyticsMetric.metric_name == metric_name,
                    AnalyticsMetric.time_bucket == time_bucket,
                    AnalyticsMetric.bucket_start == bucket_start
                )
            ).first()

            if existing_metric:
                # Update existing metric
                existing_metric.metric_value = value
                existing_metric.updated_at = datetime.utcnow()
                metric = existing_metric
            else:
                # Create new metric
                metric = AnalyticsMetric(
                    tenant_id=tenant_id,
                    metric_name=metric_name,
                    metric_value=value,
                    time_bucket=time_bucket,
                    bucket_start=bucket_start,
                    bucket_end=bucket_end,
                    dimensions=dimensions or {},
                    source=source
                )
                self.db.add(metric)

            self.db.commit()
            self.db.refresh(metric)
            return metric

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error storing metric: {e}")
            raise

    def get_metrics(self, tenant_id: UUID, metric_names: List[str],
                   time_bucket: str = 'day', days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get metrics data for dashboard
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            metrics_data = {}

            for metric_name in metric_names:
                metrics = self.db.query(AnalyticsMetric).filter(
                    and_(
                        AnalyticsMetric.tenant_id == tenant_id,
                        AnalyticsMetric.metric_name == metric_name,
                        AnalyticsMetric.time_bucket == time_bucket,
                        AnalyticsMetric.bucket_start >= start_date,
                        AnalyticsMetric.bucket_end <= end_date
                    )
                ).order_by(AnalyticsMetric.bucket_start).all()

                metrics_data[metric_name] = [
                    {
                        'date': metric.bucket_start.isoformat(),
                        'value': metric.metric_value,
                        'bucket_start': metric.bucket_start.isoformat(),
                        'bucket_end': metric.bucket_end.isoformat()
                    }
                    for metric in metrics
                ]

            return metrics_data

        except SQLAlchemyError as e:
            logger.error(f"Error getting metrics: {e}")
            raise

    def get_realtime_metrics(self, tenant_id: UUID, hours: int = 24) -> Dict[str, Any]:
        """
        Get real-time metrics for the last N hours
        """
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)

            # Active users in last 24 hours
            active_users = self.db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
                and_(
                    AnalyticsEvent.tenant_id == tenant_id,
                    AnalyticsEvent.timestamp >= start_time,
                    AnalyticsEvent.user_id.isnot(None)
                )
            ).scalar() or 0

            # Recent events
            recent_events = self.db.query(func.count(AnalyticsEvent.id)).filter(
                and_(
                    AnalyticsEvent.tenant_id == tenant_id,
                    AnalyticsEvent.timestamp >= start_time
                )
            ).scalar() or 0

            # Recent errors
            recent_errors = self.db.query(func.count(AnalyticsEvent.id)).filter(
                and_(
                    AnalyticsEvent.tenant_id == tenant_id,
                    AnalyticsEvent.event_type == 'error',
                    AnalyticsEvent.timestamp >= start_time
                )
            ).scalar() or 0

            return {
                'active_users_24h': active_users,
                'events_last_24h': recent_events,
                'errors_last_24h': recent_errors,
                'timestamp': datetime.utcnow().isoformat()
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting realtime metrics: {e}")
            raise

    def create_dashboard(self, tenant_id: UUID, user_id: UUID, name: str,
                        description: Optional[str] = None, config: Dict[str, Any] = None,
                        is_public: str = 'private') -> AnalyticsDashboard:
        """
        Create a new dashboard
        """
        try:
            dashboard = AnalyticsDashboard(
                tenant_id=tenant_id,
                user_id=user_id,
                name=name,
                description=description,
                config=config or {},
                is_public=is_public
            )

            self.db.add(dashboard)
            self.db.commit()
            self.db.refresh(dashboard)

            logger.info(f"Created dashboard: {name} for tenant {tenant_id}")
            return dashboard

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating dashboard: {e}")
            raise

    def get_dashboards(self, tenant_id: UUID, user_id: Optional[UUID] = None) -> List[AnalyticsDashboard]:
        """
        Get dashboards for a tenant/user
        """
        try:
            query = self.db.query(AnalyticsDashboard).filter(
                AnalyticsDashboard.tenant_id == tenant_id
            )

            if user_id:
                query = query.filter(
                    or_(
                        AnalyticsDashboard.user_id == user_id,
                        AnalyticsDashboard.is_public.in_(['tenant', 'public'])
                    )
                )
            else:
                query = query.filter(AnalyticsDashboard.is_public == 'public')

            return query.order_by(desc(AnalyticsDashboard.updated_at)).all()

        except SQLAlchemyError as e:
            logger.error(f"Error getting dashboards: {e}")
            raise


# Utility functions for background tasks
def collect_all_tenants_daily_metrics(db: Session) -> Dict[str, Any]:
    """
    Collect daily metrics for all tenants (background task)
    """
    from app.models.tenant import Tenant

    results = {}
    service = AnalyticsService(db)

    try:
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()

        for tenant in tenants:
            try:
                metrics = service.collect_daily_metrics(tenant.id)
                results[str(tenant.id)] = metrics
            except Exception as e:
                logger.error(f"Error collecting metrics for tenant {tenant.id}: {e}")
                results[str(tenant.id)] = {'error': str(e)}

        return results

    except SQLAlchemyError as e:
        logger.error(f"Error in daily metrics collection: {e}")
        raise


def cleanup_old_analytics_data(db: Session, days_to_keep: int = 90) -> int:
    """
    Clean up old analytics data beyond retention period
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Delete old events
        events_deleted = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.timestamp < cutoff_date
        ).delete()

        # Delete old metrics (keep aggregated data)
        metrics_deleted = db.query(AnalyticsMetric).filter(
            and_(
                AnalyticsMetric.time_bucket == 'hour',
                AnalyticsMetric.bucket_start < cutoff_date
            )
        ).delete()

        db.commit()

        total_deleted = events_deleted + metrics_deleted
        logger.info(f"Cleaned up {total_deleted} old analytics records")

        return total_deleted

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error cleaning up analytics data: {e}")
        raise