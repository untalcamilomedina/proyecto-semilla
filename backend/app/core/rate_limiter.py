"""
Advanced Rate Limiting with Machine Learning
Core logic for intelligent rate limiting system
"""

import asyncio
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict
import logging

from app.core.config import settings
from app.core.logging import get_logger
from app.ml.rate_limiting.models import RequestClassifier, AbuseDetector
from app.ml.rate_limiting.features import FeatureExtractor
from app.ml.rate_limiting.trainer import ModelTrainer

logger = get_logger(__name__)


class AdaptiveRateLimiter:
    """
    Advanced rate limiter with ML-powered decision making
    Adapts limits based on user behavior and tenant requirements
    """

    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.classifier = RequestClassifier()
        self.abuse_detector = AbuseDetector()
        self.feature_extractor = FeatureExtractor()
        self.trainer = ModelTrainer()

        # Rate limit configurations by tenant
        self.tenant_configs = self._load_tenant_configs()

        # Cache for recent requests (for feature extraction)
        self.request_cache = defaultdict(list)
        self.cache_max_size = 1000

        # Whitelist and blacklist
        self.whitelist = set()
        self.blacklist = set()
        self._load_lists()

    def _get_redis_client(self) -> Optional[redis.Redis]:
        """Get Redis client for caching and rate limiting"""
        try:
            return redis.from_url(settings.REDIS_URL)
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            return None

    def _load_tenant_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load rate limiting configurations for each tenant"""
        # Default configuration
        default_config = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'burst_limit': 10,
            'adaptive_enabled': True,
            'ml_threshold': 0.7,
            'block_duration_minutes': 15
        }

        # In production, load from database or config file
        # For now, return default config for all tenants
        return {'default': default_config}

    def _load_lists(self):
        """Load whitelist and blacklist from Redis"""
        if not self.redis_client:
            return

        try:
            # Load whitelist
            whitelist_data = self.redis_client.get('rate_limit:whitelist')
            if whitelist_data:
                self.whitelist = set(json.loads(whitelist_data))

            # Load blacklist
            blacklist_data = self.redis_client.get('rate_limit:blacklist')
            if blacklist_data:
                self.blacklist = set(json.loads(blacklist_data))

        except Exception as e:
            logger.error(f"Failed to load whitelist/blacklist: {e}")

    def _save_lists(self):
        """Save whitelist and blacklist to Redis"""
        if not self.redis_client:
            return

        try:
            self.redis_client.set('rate_limit:whitelist', json.dumps(list(self.whitelist)))
            self.redis_client.set('rate_limit:blacklist', json.dumps(list(self.blacklist)))
        except Exception as e:
            logger.error(f"Failed to save whitelist/blacklist: {e}")

    async def check_rate_limit(self, request_data: Dict[str, Any],
                             tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if request should be rate limited using ML analysis

        Args:
            request_data: Request information (IP, path, method, etc.)
            tenant_id: Tenant identifier for multi-tenant limits

        Returns:
            Dict with decision and metadata
        """
        ip_address = request_data.get('ip_address', 'unknown')
        user_id = request_data.get('user_id')
        tenant_id = tenant_id or 'default'

        # Check whitelist/blacklist first
        if ip_address in self.whitelist:
            return self._allow_request("whitelisted", request_data)

        if ip_address in self.blacklist:
            return self._block_request("blacklisted", request_data)

        # Get tenant configuration
        config = self.tenant_configs.get(tenant_id, self.tenant_configs['default'])

        # Check basic rate limits
        basic_limit_result = await self._check_basic_limits(ip_address, user_id, config)
        if not basic_limit_result['allowed']:
            return basic_limit_result

        # If ML is enabled, perform advanced analysis
        if config.get('adaptive_enabled', True):
            ml_result = await self._check_ml_analysis(request_data, tenant_id, config)
            if not ml_result['allowed']:
                return ml_result

        # Update request tracking
        await self._track_request(request_data, tenant_id)

        return self._allow_request("within_limits", request_data)

    async def _check_basic_limits(self, ip_address: str, user_id: Optional[str],
                                config: Dict[str, Any]) -> Dict[str, Any]:
        """Check basic rate limits (requests per minute/hour)"""
        if not self.redis_client:
            return {'allowed': True, 'reason': 'no_redis'}

        try:
            # Create rate limit keys
            ip_key = f"rate_limit:ip:{ip_address}"
            user_key = f"rate_limit:user:{user_id}" if user_id else None

            # Check IP-based limits
            ip_limits = await self._check_redis_limits(ip_key, config)
            if not ip_limits['allowed']:
                return {
                    'allowed': False,
                    'reason': 'ip_limit_exceeded',
                    'limit_type': ip_limits['limit_type'],
                    'retry_after': ip_limits['retry_after']
                }

            # Check user-based limits if user_id provided
            if user_key:
                user_limits = await self._check_redis_limits(user_key, config)
                if not user_limits['allowed']:
                    return {
                        'allowed': False,
                        'reason': 'user_limit_exceeded',
                        'limit_type': user_limits['limit_type'],
                        'retry_after': user_limits['retry_after']
                    }

            return {'allowed': True}

        except Exception as e:
            logger.error(f"Basic limit check error: {e}")
            return {'allowed': True, 'reason': 'error'}

    async def _check_redis_limits(self, key: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check rate limits in Redis"""
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()

            # Check minute limit
            minute_key = f"{key}:minute"
            pipe.get(minute_key)
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)

            # Check hour limit
            hour_key = f"{key}:hour"
            pipe.get(hour_key)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)

            # Check burst limit
            burst_key = f"{key}:burst"
            pipe.get(burst_key)
            pipe.incr(burst_key)
            pipe.expire(burst_key, 10)  # 10 second burst window

            results = pipe.execute()

            minute_count = int(results[1])
            hour_count = int(results[3])
            burst_count = int(results[5])

            # Check limits
            if burst_count > config.get('burst_limit', 10):
                return {
                    'allowed': False,
                    'limit_type': 'burst',
                    'retry_after': 10
                }

            if minute_count > config.get('requests_per_minute', 60):
                return {
                    'allowed': False,
                    'limit_type': 'minute',
                    'retry_after': 60
                }

            if hour_count > config.get('requests_per_hour', 1000):
                return {
                    'allowed': False,
                    'limit_type': 'hour',
                    'retry_after': 3600
                }

            return {'allowed': True}

        except Exception as e:
            logger.error(f"Redis limit check error: {e}")
            return {'allowed': True}

    async def _check_ml_analysis(self, request_data: Dict[str, Any],
                               tenant_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform ML-based analysis for rate limiting decision"""
        try:
            # Get historical requests for context
            historical_requests = self._get_historical_requests(
                request_data.get('ip_address', 'unknown')
            )

            # Extract features
            features = self.feature_extractor.extract_request_features(
                request_data, historical_requests
            )

            # Classify request
            prediction, confidence = self.classifier.predict(features)

            # Check abuse patterns
            abuse_pattern = {
                'ip_address': request_data.get('ip_address'),
                'total_requests': len(historical_requests) + 1,
                'unique_endpoints': len(set(req.get('path', '/') for req in historical_requests)),
                'time_span_minutes': self._calculate_time_span(historical_requests),
                'burst_events': self._count_burst_events(historical_requests),
                'failed_requests_ratio': self._calculate_failed_ratio(historical_requests)
            }

            is_anomaly, anomaly_score = self.abuse_detector.detect_anomaly(abuse_pattern)

            # Decision logic
            ml_threshold = config.get('ml_threshold', 0.7)

            if prediction == "suspicious" and confidence > ml_threshold:
                return {
                    'allowed': False,
                    'reason': 'ml_suspicious',
                    'confidence': confidence,
                    'prediction': prediction
                }

            if is_anomaly and anomaly_score > ml_threshold:
                return {
                    'allowed': False,
                    'reason': 'ml_anomaly',
                    'anomaly_score': anomaly_score
                }

            return {'allowed': True}

        except Exception as e:
            logger.error(f"ML analysis error: {e}")
            return {'allowed': True, 'reason': 'ml_error'}

    async def _track_request(self, request_data: Dict[str, Any], tenant_id: str):
        """Track request for future ML analysis"""
        try:
            # Add timestamp
            request_data['timestamp'] = datetime.utcnow().isoformat()
            request_data['tenant_id'] = tenant_id

            # Add to cache
            ip_address = request_data.get('ip_address', 'unknown')
            self.request_cache[ip_address].append(request_data)

            # Maintain cache size
            if len(self.request_cache[ip_address]) > self.cache_max_size:
                self.request_cache[ip_address] = self.request_cache[ip_address][-self.cache_max_size:]

            # Store in Redis for persistence (optional)
            if self.redis_client:
                cache_key = f"rate_limit:requests:{ip_address}"
                self.redis_client.lpush(cache_key, json.dumps(request_data))
                self.redis_client.ltrim(cache_key, 0, self.cache_max_size - 1)
                self.redis_client.expire(cache_key, 3600)  # 1 hour TTL

        except Exception as e:
            logger.error(f"Request tracking error: {e}")

    def _get_historical_requests(self, ip_address: str) -> List[Dict[str, Any]]:
        """Get historical requests for IP address"""
        # Try cache first
        if ip_address in self.request_cache:
            return self.request_cache[ip_address]

        # Try Redis
        if self.redis_client:
            try:
                cache_key = f"rate_limit:requests:{ip_address}"
                cached_requests = self.redis_client.lrange(cache_key, 0, -1)
                if cached_requests:
                    return [json.loads(req) for req in cached_requests]
            except Exception as e:
                logger.error(f"Redis cache read error: {e}")

        return []

    def _calculate_time_span(self, requests: List[Dict[str, Any]]) -> float:
        """Calculate time span of requests in minutes"""
        if not requests:
            return 0

        timestamps = []
        for req in requests:
            try:
                timestamps.append(datetime.fromisoformat(req.get('timestamp', '2000-01-01T00:00:00')))
            except:
                continue

        if not timestamps:
            return 0

        time_span = max(timestamps) - min(timestamps)
        return time_span.total_seconds() / 60

    def _count_burst_events(self, requests: List[Dict[str, Any]]) -> int:
        """Count burst events in request history"""
        if len(requests) < 5:
            return 0

        burst_count = 0
        window_size = 10  # 10 second window

        # Sort by timestamp
        sorted_requests = sorted(requests, key=lambda x: x.get('timestamp', ''))

        for i in range(len(sorted_requests) - 4):
            window_requests = sorted_requests[i:i+5]
            if self._is_burst_window(window_requests, window_size):
                burst_count += 1

        return burst_count

    def _is_burst_window(self, requests: List[Dict[str, Any]], window_size: int) -> bool:
        """Check if requests in window constitute a burst"""
        if len(requests) < 5:
            return False

        try:
            first_time = datetime.fromisoformat(requests[0].get('timestamp', '2000-01-01T00:00:00'))
            last_time = datetime.fromisoformat(requests[-1].get('timestamp', '2000-01-01T00:00:00'))

            time_diff = (last_time - first_time).total_seconds()
            return time_diff <= window_size
        except:
            return False

    def _calculate_failed_ratio(self, requests: List[Dict[str, Any]]) -> float:
        """Calculate ratio of failed requests"""
        if not requests:
            return 0

        failed_count = 0
        for req in requests:
            status_code = req.get('status_code', 200)
            if status_code >= 400:
                failed_count += 1

        return failed_count / len(requests)

    def _allow_request(self, reason: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create allow response"""
        return {
            'allowed': True,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request_data.get('ip_address'),
            'user_agent': request_data.get('user_agent')
        }

    def _block_request(self, reason: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create block response"""
        return {
            'allowed': False,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request_data.get('ip_address'),
            'user_agent': request_data.get('user_agent')
        }

    # Public methods for management

    def add_to_whitelist(self, ip_address: str):
        """Add IP to whitelist"""
        self.whitelist.add(ip_address)
        self.blacklist.discard(ip_address)  # Remove from blacklist if present
        self._save_lists()
        logger.info(f"Added {ip_address} to whitelist")

    def add_to_blacklist(self, ip_address: str):
        """Add IP to blacklist"""
        self.blacklist.add(ip_address)
        self.whitelist.discard(ip_address)  # Remove from whitelist if present
        self._save_lists()
        logger.info(f"Added {ip_address} to blacklist")

    def remove_from_whitelist(self, ip_address: str):
        """Remove IP from whitelist"""
        self.whitelist.discard(ip_address)
        self._save_lists()
        logger.info(f"Removed {ip_address} from whitelist")

    def remove_from_blacklist(self, ip_address: str):
        """Remove IP from blacklist"""
        self.blacklist.discard(ip_address)
        self._save_lists()
        logger.info(f"Removed {ip_address} from blacklist")

    def update_tenant_config(self, tenant_id: str, config: Dict[str, Any]):
        """Update rate limiting configuration for tenant"""
        self.tenant_configs[tenant_id] = config
        logger.info(f"Updated config for tenant {tenant_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        return {
            'whitelist_count': len(self.whitelist),
            'blacklist_count': len(self.blacklist),
            'tenant_configs': len(self.tenant_configs),
            'cache_size': sum(len(requests) for requests in self.request_cache.values()),
            'ml_models_loaded': {
                'classifier': len(self.classifier.models) > 0,
                'abuse_detector': self.abuse_detector.model is not None
            }
        }

    async def cleanup_expired_data(self):
        """Clean up expired rate limiting data"""
        if not self.redis_client:
            return

        try:
            # This would be called periodically to clean up old data
            # Implementation depends on specific cleanup requirements
            pass
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global rate limiter instance
rate_limiter = AdaptiveRateLimiter()