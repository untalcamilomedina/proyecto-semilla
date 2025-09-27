"""
Analytics API endpoints for Proyecto Semilla
Provides REST API for analytics queries, dashboards, and reports
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.analytics import AnalyticsEvent, AnalyticsMetric, AnalyticsDashboard, AnalyticsReport
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    MetricsResponse,
    RealtimeMetricsResponse,
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    ReportCreate,
    ReportResponse
)

router = APIRouter()


@router.post("/events", response_model=AnalyticsEventResponse)
async def track_event(
    event: AnalyticsEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track an analytics event
    """
    service = AnalyticsService(db)

    try:
        tracked_event = service.track_event(
            tenant_id=current_user.tenant_id,
            event_type=event.event_type,
            event_name=event.event_name,
            user_id=current_user.id,
            session_id=event.session_id,
            properties=event.properties,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            metadata=event.metadata
        )

        return AnalyticsEventResponse.from_orm(tracked_event)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking event: {str(e)}")


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    metric_names: List[str] = Query(..., description="List of metric names to retrieve"),
    time_bucket: str = Query("day", description="Time bucket: hour, day, week, month"),
    days: int = Query(30, description="Number of days of data to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics metrics data
    """
    service = AnalyticsService(db)

    try:
        metrics_data = service.get_metrics(
            tenant_id=current_user.tenant_id,
            metric_names=metric_names,
            time_bucket=time_bucket,
            days=days
        )

        return MetricsResponse(
            tenant_id=current_user.tenant_id,
            time_bucket=time_bucket,
            days=days,
            metrics=metrics_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")


@router.get("/metrics/realtime", response_model=RealtimeMetricsResponse)
async def get_realtime_metrics(
    hours: int = Query(24, description="Number of hours for real-time data"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get real-time analytics metrics
    """
    service = AnalyticsService(db)

    try:
        realtime_data = service.get_realtime_metrics(
            tenant_id=current_user.tenant_id,
            hours=hours
        )

        return RealtimeMetricsResponse(
            tenant_id=current_user.tenant_id,
            hours=hours,
            **realtime_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving realtime metrics: {str(e)}")


@router.post("/dashboards", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new analytics dashboard
    """
    service = AnalyticsService(db)

    try:
        new_dashboard = service.create_dashboard(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            name=dashboard.name,
            description=dashboard.description,
            config=dashboard.config,
            is_public=dashboard.is_public
        )

        return DashboardResponse.from_orm(new_dashboard)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating dashboard: {str(e)}")


@router.get("/dashboards", response_model=List[DashboardResponse])
async def get_dashboards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's dashboards
    """
    service = AnalyticsService(db)

    try:
        dashboards = service.get_dashboards(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id
        )

        return [DashboardResponse.from_orm(dashboard) for dashboard in dashboards]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboards: {str(e)}")


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific dashboard
    """
    dashboard = db.query(AnalyticsDashboard).filter(
        AnalyticsDashboard.id == dashboard_id,
        AnalyticsDashboard.tenant_id == current_user.tenant_id
    ).first()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Check permissions
    if (dashboard.user_id != current_user.id and
        dashboard.is_public not in ['tenant', 'public']):
        raise HTTPException(status_code=403, detail="Access denied")

    return DashboardResponse.from_orm(dashboard)


@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    dashboard_update: DashboardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a dashboard
    """
    dashboard = db.query(AnalyticsDashboard).filter(
        AnalyticsDashboard.id == dashboard_id,
        AnalyticsDashboard.tenant_id == current_user.tenant_id,
        AnalyticsDashboard.user_id == current_user.id
    ).first()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Update fields
    update_data = dashboard_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dashboard, field, value)

    dashboard.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(dashboard)
        return DashboardResponse.from_orm(dashboard)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating dashboard: {str(e)}")


@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a dashboard
    """
    dashboard = db.query(AnalyticsDashboard).filter(
        AnalyticsDashboard.id == dashboard_id,
        AnalyticsDashboard.tenant_id == current_user.tenant_id,
        AnalyticsDashboard.user_id == current_user.id
    ).first()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    try:
        db.delete(dashboard)
        db.commit()
        return {"message": "Dashboard deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting dashboard: {str(e)}")


@router.post("/collect-metrics")
async def collect_daily_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger daily metrics collection (admin only)
    """
    # TODO: Add admin permission check
    service = AnalyticsService(db)

    try:
        metrics = service.collect_daily_metrics(current_user.tenant_id)
        return {
            "message": "Metrics collected successfully",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting metrics: {str(e)}")


@router.get("/events")
async def get_events(
    event_type: Optional[str] = None,
    limit: int = Query(100, description="Maximum number of events to return"),
    offset: int = Query(0, description="Number of events to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics events with optional filtering
    """
    query = db.query(AnalyticsEvent).filter(
        AnalyticsEvent.tenant_id == current_user.tenant_id
    )

    if event_type:
        query = query.filter(AnalyticsEvent.event_type == event_type)

    events = query.order_by(AnalyticsEvent.timestamp.desc()).offset(offset).limit(limit).all()

    return {
        "events": [AnalyticsEventResponse.from_orm(event) for event in events],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(7, description="Number of days for summary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of key analytics metrics
    """
    service = AnalyticsService(db)

    try:
        # Get metrics for the period
        metric_names = ['active_users', 'articles_published', 'api_requests', 'errors', 'page_views']
        metrics_data = service.get_metrics(
            tenant_id=current_user.tenant_id,
            metric_names=metric_names,
            time_bucket='day',
            days=days
        )

        # Calculate totals and trends
        summary = {}
        for metric_name in metric_names:
            data_points = metrics_data.get(metric_name, [])
            if data_points:
                values = [point['value'] for point in data_points]
                total = sum(values)
                avg = total / len(values) if values else 0

                # Simple trend calculation (compare first half vs second half)
                mid_point = len(values) // 2
                first_half_avg = sum(values[:mid_point]) / mid_point if mid_point > 0 else 0
                second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point) if mid_point < len(values) else 0

                trend = "stable"
                if second_half_avg > first_half_avg * 1.1:
                    trend = "up"
                elif second_half_avg < first_half_avg * 0.9:
                    trend = "down"

                summary[metric_name] = {
                    "total": total,
                    "average": avg,
                    "trend": trend,
                    "data_points": len(data_points)
                }
            else:
                summary[metric_name] = {
                    "total": 0,
                    "average": 0,
                    "trend": "no_data",
                    "data_points": 0
                }

        return {
            "tenant_id": current_user.tenant_id,
            "period_days": days,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")