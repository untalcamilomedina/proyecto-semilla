"""
Rate Limiting Management Endpoints
API endpoints for managing advanced rate limiting system
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.services.rate_limit_service import rate_limit_service
from app.middleware.advanced_rate_limit import get_rate_limit_stats
from app.models.user import User
from app.services.permission_service import require_permission, has_permission

logger = get_logger(__name__)

router = APIRouter()


@router.get("/status", response_model=Dict[str, Any])
async def get_rate_limit_status(
    ip_address: Optional[str] = Query(None, description="IP address to check"),
    user_id: Optional[str] = Query(None, description="User ID to check"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID context"),
    current_user: User = Depends(require_permission("rate_limit:read"))
):
    """
    Get current rate limiting status for an IP/user/tenant combination

    Requires rate_limit:read permission
    """
    try:
        if not ip_address and not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either ip_address or user_id must be provided"
            )

        status_data = await rate_limit_service.get_rate_limit_status(
            ip_address=ip_address,
            user_id=user_id,
            tenant_id=tenant_id
        )

        return status_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit status"
        )


@router.post("/whitelist", response_model=Dict[str, Any])
async def manage_whitelist(
    action: str = Query(..., description="Action: add or remove", regex="^(add|remove)$"),
    ip_address: str = Query(..., description="IP address to manage"),
    reason: Optional[str] = Query(None, description="Reason for the action"),
    current_user: User = Depends(require_permission("rate_limit:manage"))
):
    """
    Add or remove IP address from whitelist

    Requires rate_limit:manage permission
    """
    try:
        result = await rate_limit_service.manage_whitelist_blacklist(
            action=f"{action}_whitelist",
            ip_address=ip_address,
            reason=reason
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Operation failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error managing whitelist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to manage whitelist"
        )


@router.post("/blacklist", response_model=Dict[str, Any])
async def manage_blacklist(
    action: str = Query(..., description="Action: add or remove", regex="^(add|remove)$"),
    ip_address: str = Query(..., description="IP address to manage"),
    reason: Optional[str] = Query(None, description="Reason for the action"),
    current_user: User = Depends(require_permission("rate_limit:manage"))
):
    """
    Add or remove IP address from blacklist

    Requires rate_limit:manage permission
    """
    try:
        result = await rate_limit_service.manage_whitelist_blacklist(
            action=f"{action}_blacklist",
            ip_address=ip_address,
            reason=reason
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Operation failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error managing blacklist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to manage blacklist"
        )


@router.put("/tenant-config", response_model=Dict[str, Any])
async def update_tenant_config(
    tenant_id: str = Query(..., description="Tenant ID to update"),
    requests_per_minute: Optional[int] = Query(60, description="Requests per minute limit"),
    requests_per_hour: Optional[int] = Query(1000, description="Requests per hour limit"),
    burst_limit: Optional[int] = Query(10, description="Burst request limit"),
    adaptive_enabled: Optional[bool] = Query(True, description="Enable adaptive ML-based limiting"),
    ml_threshold: Optional[float] = Query(0.7, description="ML confidence threshold"),
    block_duration_minutes: Optional[int] = Query(15, description="Block duration in minutes"),
    current_user: User = Depends(require_permission("rate_limit:configure"))
):
    """
    Update rate limiting configuration for a tenant

    Requires rate_limit:configure permission
    """
    try:
        config = {
            'requests_per_minute': requests_per_minute,
            'requests_per_hour': requests_per_hour,
            'burst_limit': burst_limit,
            'adaptive_enabled': adaptive_enabled,
            'ml_threshold': ml_threshold,
            'block_duration_minutes': block_duration_minutes
        }

        result = await rate_limit_service.update_tenant_configuration(
            tenant_id=tenant_id,
            config=config
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Configuration update failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant configuration"
        )


@router.get("/statistics", response_model=Dict[str, Any])
async def get_system_statistics(
    current_user: User = Depends(require_permission("rate_limit:read"))
):
    """
    Get comprehensive system statistics for monitoring

    Requires rate_limit:read permission
    """
    try:
        stats = await rate_limit_service.get_system_statistics()
        return stats

    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system statistics"
        )


@router.post("/train-models", response_model=Dict[str, Any])
async def train_ml_models(
    force_retrain: bool = Query(False, description="Force full retraining"),
    current_user: User = Depends(require_permission("rate_limit:configure"))
):
    """
    Train or update ML models with recent data

    Requires rate_limit:configure permission
    """
    try:
        result = await rate_limit_service.train_ml_models(force_retrain=force_retrain)
        return result

    except Exception as e:
        logger.error(f"Error training ML models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to train ML models"
        )


@router.post("/reset-limits", response_model=Dict[str, Any])
async def reset_rate_limits(
    ip_address: Optional[str] = Query(None, description="IP address to reset"),
    user_id: Optional[str] = Query(None, description="User ID to reset"),
    current_user: User = Depends(require_permission("rate_limit:manage"))
):
    """
    Reset rate limits for specific IP or user

    Requires rate_limit:manage permission
    """
    try:
        if not ip_address and not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either ip_address or user_id must be provided"
            )

        result = await rate_limit_service.reset_rate_limits(
            ip_address=ip_address,
            user_id=user_id
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Reset operation failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting rate limits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset rate limits"
        )


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_rate_limiting_dashboard(
    hours: int = Query(24, description="Hours of data to include", ge=1, le=168),
    current_user: User = Depends(require_permission("rate_limit:read"))
):
    """
    Get dashboard data for rate limiting monitoring

    Requires rate_limit:read permission
    """
    try:
        # Get basic statistics
        stats = get_rate_limit_stats()

        # Add time-based metrics
        now = datetime.utcnow()
        time_window_start = now.replace(hour=now.hour - hours, minute=0, second=0, microsecond=0)

        dashboard_data = {
            'timestamp': now.isoformat(),
            'time_window_hours': hours,
            'system_stats': stats,
            'time_window_start': time_window_start.isoformat(),
            'alerts': [],  # Would be populated with active alerts
            'recent_blocks': [],  # Would be populated with recent blocks
            'top_offenders': []  # Would be populated with top offending IPs
        }

        return dashboard_data

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )