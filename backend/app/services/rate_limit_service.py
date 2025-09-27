"""
Rate Limiting Service
Service layer for managing advanced rate limiting operations
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func

from app.core.database import get_db
from app.core.rate_limiter import rate_limiter
from app.core.logging import get_logger
from app.ml.rate_limiting.trainer import ModelTrainer
from app.models.user import User
from app.models.tenant import Tenant

logger = get_logger(__name__)


class RateLimitService:
    """
    Service for managing rate limiting operations
    Provides high-level interface for rate limiting management
    """

    def __init__(self):
        self.trainer = ModelTrainer()

    async def get_rate_limit_status(self, ip_address: str, user_id: Optional[str] = None,
                                  tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current rate limiting status for an IP/user/tenant combination

        Args:
            ip_address: IP address to check
            user_id: Optional user ID
            tenant_id: Optional tenant ID

        Returns:
            Dictionary with current status and limits
        """
        try:
            # Get current counts from Redis
            current_counts = await self._get_current_counts(ip_address, user_id)

            # Get tenant configuration
            tenant_config = self._get_tenant_config(tenant_id)

            # Get historical data for analysis
            historical_data = self._get_historical_data(ip_address, user_id)

            # Calculate risk score
            risk_score = await self._calculate_risk_score(ip_address, user_id, historical_data)

            return {
                'ip_address': ip_address,
                'user_id': user_id,
                'tenant_id': tenant_id,
                'current_counts': current_counts,
                'limits': tenant_config,
                'historical_requests': len(historical_data),
                'risk_score': risk_score,
                'is_whitelisted': ip_address in rate_limiter.whitelist,
                'is_blacklisted': ip_address in rate_limiter.blacklist,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {'error': str(e)}

    async def _get_current_counts(self, ip_address: str, user_id: Optional[str]) -> Dict[str, Any]:
        """Get current request counts from Redis"""
        counts = {
            'ip_minute': 0,
            'ip_hour': 0,
            'ip_burst': 0,
            'user_minute': 0,
            'user_hour': 0,
            'user_burst': 0
        }

        if not rate_limiter.redis_client:
            return counts

        try:
            # Get IP counts
            ip_keys = [
                f"rate_limit:ip:{ip_address}:minute",
                f"rate_limit:ip:{ip_address}:hour",
                f"rate_limit:ip:{ip_address}:burst"
            ]

            for i, key in enumerate(ip_keys):
                value = rate_limiter.redis_client.get(key)
                if value:
                    key_name = ['ip_minute', 'ip_hour', 'ip_burst'][i]
                    counts[key_name] = int(value)

            # Get user counts if user_id provided
            if user_id:
                user_keys = [
                    f"rate_limit:user:{user_id}:minute",
                    f"rate_limit:user:{user_id}:hour",
                    f"rate_limit:user:{user_id}:burst"
                ]

                for i, key in enumerate(user_keys):
                    value = rate_limiter.redis_client.get(key)
                    if value:
                        key_name = ['user_minute', 'user_hour', 'user_burst'][i]
                        counts[key_name] = int(value)

        except Exception as e:
            logger.error(f"Error getting current counts: {e}")

        return counts

    def _get_tenant_config(self, tenant_id: Optional[str]) -> Dict[str, Any]:
        """Get rate limiting configuration for tenant"""
        if tenant_id and tenant_id in rate_limiter.tenant_configs:
            return rate_limiter.tenant_configs[tenant_id]

        return rate_limiter.tenant_configs.get('default', {})

    def _get_historical_data(self, ip_address: str, user_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get historical request data for analysis"""
        return rate_limiter._get_historical_requests(ip_address)

    async def _calculate_risk_score(self, ip_address: str, user_id: Optional[str],
                                  historical_data: List[Dict[str, Any]]) -> float:
        """Calculate risk score based on historical behavior"""
        if not historical_data:
            return 0.0

        try:
            # Simple risk scoring based on patterns
            risk_factors = []

            # Factor 1: Request frequency
            total_requests = len(historical_data)
            time_span_hours = rate_limiter._calculate_time_span(historical_data) / 60
            if time_span_hours > 0:
                requests_per_hour = total_requests / time_span_hours
                if requests_per_hour > 100:
                    risk_factors.append(0.8)
                elif requests_per_hour > 50:
                    risk_factors.append(0.4)
                else:
                    risk_factors.append(0.1)

            # Factor 2: Failed request ratio
            failed_ratio = rate_limiter._calculate_failed_ratio(historical_data)
            risk_factors.append(min(failed_ratio, 1.0))

            # Factor 3: Burst events
            burst_events = rate_limiter._count_burst_events(historical_data)
            burst_risk = min(burst_events / 10, 1.0)  # Normalize
            risk_factors.append(burst_risk)

            # Factor 4: Endpoint diversity (lower diversity = higher risk)
            if historical_data:
                unique_endpoints = len(set(req.get('path', '/') for req in historical_data))
                diversity_ratio = unique_endpoints / len(historical_data)
                diversity_risk = 1.0 - diversity_ratio
                risk_factors.append(diversity_risk)

            # Calculate weighted average
            if risk_factors:
                return sum(risk_factors) / len(risk_factors)

            return 0.0

        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.0

    async def manage_whitelist_blacklist(self, action: str, ip_address: str,
                                       reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Manage whitelist and blacklist operations

        Args:
            action: 'add_whitelist', 'remove_whitelist', 'add_blacklist', 'remove_blacklist'
            ip_address: IP address to manage
            reason: Optional reason for the action

        Returns:
            Result of the operation
        """
        try:
            result = {'success': False, 'action': action, 'ip_address': ip_address}

            if action == 'add_whitelist':
                rate_limiter.add_to_whitelist(ip_address)
                result['success'] = True
                result['message'] = f"Added {ip_address} to whitelist"

            elif action == 'remove_whitelist':
                rate_limiter.remove_from_whitelist(ip_address)
                result['success'] = True
                result['message'] = f"Removed {ip_address} from whitelist"

            elif action == 'add_blacklist':
                rate_limiter.add_to_blacklist(ip_address)
                result['success'] = True
                result['message'] = f"Added {ip_address} to blacklist"

            elif action == 'remove_blacklist':
                rate_limiter.remove_from_blacklist(ip_address)
                result['success'] = True
                result['message'] = f"Removed {ip_address} from blacklist"

            else:
                result['message'] = f"Unknown action: {action}"

            if result['success'] and reason:
                result['reason'] = reason

            # Log the action
            logger.info(f"Whitelist/blacklist action: {action} for {ip_address}",
                       reason=reason, success=result['success'])

            return result

        except Exception as e:
            logger.error(f"Error managing whitelist/blacklist: {e}")
            return {'success': False, 'error': str(e)}

    async def update_tenant_configuration(self, tenant_id: str, config: Dict[str, Any],
                                        updated_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Update rate limiting configuration for a tenant

        Args:
            tenant_id: Tenant ID to update
            config: New configuration
            updated_by: User who made the update

        Returns:
            Result of the update
        """
        try:
            # Validate configuration
            validation_result = self._validate_tenant_config(config)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Invalid configuration',
                    'details': validation_result['errors']
                }

            # Update configuration
            rate_limiter.update_tenant_config(tenant_id, config)

            # Log the update
            logger.info(f"Updated rate limit config for tenant {tenant_id}",
                       updated_by=updated_by, config=config)

            return {
                'success': True,
                'tenant_id': tenant_id,
                'config': config,
                'updated_by': updated_by,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error updating tenant configuration: {e}")
            return {'success': False, 'error': str(e)}

    def _validate_tenant_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tenant configuration"""
        errors = []
        valid = True

        # Required fields with validation
        required_fields = {
            'requests_per_minute': (int, 1, 10000),
            'requests_per_hour': (int, 10, 100000),
            'burst_limit': (int, 1, 1000),
            'adaptive_enabled': (bool, None, None),
            'ml_threshold': (float, 0.0, 1.0),
            'block_duration_minutes': (int, 1, 1440)
        }

        for field, (field_type, min_val, max_val) in required_fields.items():
            if field not in config:
                errors.append(f"Missing required field: {field}")
                valid = False
                continue

            value = config[field]
            if not isinstance(value, field_type):
                errors.append(f"Field {field} must be of type {field_type.__name__}")
                valid = False
                continue

            if min_val is not None and value < min_val:
                errors.append(f"Field {field} must be >= {min_val}")
                valid = False

            if max_val is not None and value > max_val:
                errors.append(f"Field {field} must be <= {max_val}")
                valid = False

        return {'valid': valid, 'errors': errors}

    async def get_system_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics for monitoring

        Returns:
            Dictionary with system statistics
        """
        try:
            stats = rate_limiter.get_stats()

            # Add additional statistics
            stats.update({
                'timestamp': datetime.utcnow().isoformat(),
                'active_monitoring': True,
                'ml_models_status': self.trainer.get_model_stats()
            })

            # Get database statistics if available
            db_stats = await self._get_database_stats()
            stats.update(db_stats)

            return stats

        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {'error': str(e)}

    async def _get_database_stats(self) -> Dict[str, Any]:
        """Get database-related statistics"""
        try:
            async with get_db() as db:
                # Count total users
                user_count = await db.scalar(select(func.count()).select_from(User))

                # Count total tenants
                tenant_count = await db.scalar(select(func.count()).select_from(Tenant))

                return {
                    'total_users': user_count,
                    'total_tenants': tenant_count
                }

        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'database_error': str(e)}

    async def train_ml_models(self, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Train or update ML models with recent data

        Args:
            force_retrain: Force full retraining

        Returns:
            Training results
        """
        try:
            # Collect recent request data for training
            training_data = await self._collect_training_data()

            if not training_data:
                return {'success': False, 'message': 'No training data available'}

            # Update models
            result = self.trainer.update_models(training_data, force_retrain)

            logger.info("ML model training completed", result=result)

            return {
                'success': True,
                'message': 'ML models updated successfully',
                'result': result
            }

        except Exception as e:
            logger.error(f"Error training ML models: {e}")
            return {'success': False, 'error': str(e)}

    async def _collect_training_data(self) -> List[Dict[str, Any]]:
        """Collect recent request data for ML training"""
        # This would collect data from Redis cache and database
        # For now, return empty list as implementation depends on data storage
        return []

    async def reset_rate_limits(self, ip_address: Optional[str] = None,
                              user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Reset rate limits for specific IP or user

        Args:
            ip_address: IP address to reset (optional)
            user_id: User ID to reset (optional)

        Returns:
            Result of the reset operation
        """
        try:
            if not rate_limiter.redis_client:
                return {'success': False, 'error': 'Redis not available'}

            reset_keys = []

            if ip_address:
                reset_keys.extend([
                    f"rate_limit:ip:{ip_address}:minute",
                    f"rate_limit:ip:{ip_address}:hour",
                    f"rate_limit:ip:{ip_address}:burst"
                ])

            if user_id:
                reset_keys.extend([
                    f"rate_limit:user:{user_id}:minute",
                    f"rate_limit:user:{user_id}:hour",
                    f"rate_limit:user:{user_id}:burst"
                ])

            if not reset_keys:
                return {'success': False, 'error': 'No IP or user specified'}

            # Delete the keys
            deleted_count = rate_limiter.redis_client.delete(*reset_keys)

            logger.info(f"Reset rate limits for ip={ip_address}, user={user_id}",
                       deleted_keys=deleted_count)

            return {
                'success': True,
                'message': f'Reset {deleted_count} rate limit keys',
                'ip_address': ip_address,
                'user_id': user_id
            }

        except Exception as e:
            logger.error(f"Error resetting rate limits: {e}")
            return {'success': False, 'error': str(e)}


# Global service instance
rate_limit_service = RateLimitService()