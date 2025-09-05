"""
Advanced Security System for Proyecto Semilla
Enterprise-grade threat detection and API security monitoring
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
from collections import defaultdict, deque

from redis.asyncio import Redis
from fastapi import Request, HTTPException
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ThreatPattern:
    """Pattern for threat detection"""
    ip_address: str
    user_agent: str
    request_pattern: List[str]
    risk_score: float
    last_seen: datetime
    request_count: int = 0
    blocked_requests: int = 0


@dataclass
class SecurityMetrics:
    """Security monitoring metrics"""
    total_requests: int = 0
    blocked_requests: int = 0
    suspicious_requests: int = 0
    threats_detected: int = 0
    average_risk_score: float = 0.0
    top_threat_ips: List[str] = field(default_factory=list)


class AdvancedRateLimiter:
    """
    Advanced rate limiter with ML-based adaptive limiting
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self.base_window = 60  # 1 minute
        self.base_limit = 100
        self.burst_limit = 200
        self.threat_multiplier = 2.0

    async def check_rate_limit(
        self,
        key: str,
        user_id: Optional[int] = None,
        ip_address: str = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limit with adaptive behavior
        Returns: (allowed, metadata)
        """
        current_time = int(time.time())
        window_key = f"rate_limit:{key}:{current_time // self.base_window}"

        # Get current request count
        current_count = await self.redis.incr(window_key)
        if current_count == 1:
            await self.redis.expire(window_key, self.base_window * 2)

        # Calculate adaptive limit based on user risk
        base_limit = self.base_limit
        if user_id:
            user_risk = await self._calculate_user_risk(user_id)
            base_limit = int(self.base_limit * (1 - user_risk * 0.5))

        # Check burst limit
        burst_key = f"burst_limit:{key}:{current_time // 10}"  # 10 second windows
        burst_count = await self.redis.incr(burst_key)
        if burst_count == 1:
            await self.redis.expire(burst_key, 20)

        allowed = current_count <= base_limit and burst_count <= self.burst_limit

        metadata = {
            "current_count": current_count,
            "limit": base_limit,
            "burst_count": burst_count,
            "burst_limit": self.burst_limit,
            "window_remaining": self.base_window - (current_time % self.base_window),
            "allowed": allowed
        }

        if not allowed:
            logger.warning(f"Rate limit exceeded for key: {key}, count: {current_count}")

        return allowed, metadata

    async def _calculate_user_risk(self, user_id: int) -> float:
        """Calculate user risk score based on behavior patterns"""
        # This would integrate with user behavior analytics
        # For now, return a basic risk score
        risk_key = f"user_risk:{user_id}"
        risk_score = float(await self.redis.get(risk_key) or 0.0)
        return min(risk_score, 1.0)


class ThreatDetector:
    """
    ML-based threat detection system
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self.threat_patterns: Dict[str, ThreatPattern] = {}
        self.risk_threshold = 0.8
        self.max_patterns = 10000
        self.pattern_ttl = 3600  # 1 hour

    async def analyze_request(self, request: Request) -> Dict[str, Any]:
        """
        Analyze request for threat patterns
        Returns threat assessment
        """
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        path = str(request.url.path)
        method = request.method

        # Extract features for analysis
        features = self._extract_features(request, ip_address, user_agent, path, method)

        # Calculate risk score
        risk_score = await self._calculate_risk_score(features)

        # Update threat patterns
        await self._update_threat_patterns(ip_address, user_agent, path, risk_score)

        # Determine actions
        actions = self._determine_actions(risk_score)

        assessment = {
            "risk_score": risk_score,
            "blocked": risk_score > 0.9,
            "suspicious": risk_score > 0.7,
            "actions": actions,
            "features": features
        }

        if risk_score > self.risk_threshold:
            logger.warning(f"High risk request detected: {ip_address}, score: {risk_score:.3f}")

        return assessment

    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP address"""
        # Check for forwarded headers
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for cloudflare headers
        cf_connecting_ip = request.headers.get("cf-connecting-ip")
        if cf_connecting_ip:
            return cf_connecting_ip

        # Fallback to direct IP
        return request.client.host if request.client else "unknown"

    def _extract_features(self, request: Request, ip: str, user_agent: str, path: str, method: str) -> Dict[str, Any]:
        """Extract features for threat analysis"""
        return {
            "ip_address": ip,
            "user_agent": user_agent,
            "path": path,
            "method": method,
            "user_agent_length": len(user_agent),
            "path_depth": len(path.split("/")) - 1,
            "has_suspicious_chars": self._has_suspicious_chars(path),
            "is_common_attack_path": self._is_common_attack_path(path),
            "request_frequency": 0,  # Will be calculated separately
            "ip_reputation": 0,  # Would integrate with threat intelligence
        }

    def _has_suspicious_chars(self, path: str) -> bool:
        """Check for suspicious characters in path"""
        suspicious_chars = ["../", "..\\", "<script", "javascript:", "data:", "vbscript:"]
        return any(char in path.lower() for char in suspicious_chars)

    def _is_common_attack_path(self, path: str) -> bool:
        """Check if path matches common attack patterns"""
        attack_patterns = [
            "/wp-admin", "/wp-login", "/admin", "/phpmyadmin",
            "/.env", "/.git", "/backup", "/config",
            "/adminer", "/phpinfo", "/server-status"
        ]
        return any(pattern in path.lower() for pattern in attack_patterns)

    async def _calculate_risk_score(self, features: Dict[str, Any]) -> float:
        """Calculate risk score using simple ML-like approach"""
        score = 0.0

        # IP-based scoring
        ip_key = f"ip_requests:{features['ip_address']}"
        ip_count = int(await self.redis.get(ip_key) or 0)

        if ip_count > 1000:  # Very high frequency
            score += 0.8
        elif ip_count > 100:  # High frequency
            score += 0.4
        elif ip_count > 10:  # Moderate frequency
            score += 0.2

        # Path-based scoring
        if features['has_suspicious_chars']:
            score += 0.6
        if features['is_common_attack_path']:
            score += 0.7

        # User agent analysis
        if not features['user_agent'] or len(features['user_agent']) < 10:
            score += 0.3

        # Method analysis
        suspicious_methods = ['TRACE', 'TRACK', 'CONNECT']
        if features['method'] in suspicious_methods:
            score += 0.5

        return min(score, 1.0)

    async def _update_threat_patterns(
        self,
        ip: str,
        user_agent: str,
        path: str,
        risk_score: float
    ):
        """Update threat patterns database"""
        pattern_key = f"{ip}:{hash(user_agent)}"

        # Get existing pattern
        pattern_data = await self.redis.get(f"threat_pattern:{pattern_key}")
        if pattern_data:
            pattern = ThreatPattern(**json.loads(pattern_data))
        else:
            pattern = ThreatPattern(
                ip_address=ip,
                user_agent=user_agent,
                request_pattern=[],
                risk_score=0.0,
                last_seen=datetime.now()
            )

        # Update pattern
        pattern.request_pattern.append(path)
        pattern.risk_score = max(pattern.risk_score, risk_score)
        pattern.last_seen = datetime.now()
        pattern.request_count += 1

        if risk_score > 0.8:
            pattern.blocked_requests += 1

        # Keep only recent patterns
        if len(pattern.request_pattern) > 10:
            pattern.request_pattern = pattern.request_pattern[-10:]

        # Store pattern
        await self.redis.setex(
            f"threat_pattern:{pattern_key}",
            self.pattern_ttl,
            json.dumps(pattern.__dict__, default=str)
        )

    def _determine_actions(self, risk_score: float) -> List[str]:
        """Determine actions based on risk score"""
        actions = []

        if risk_score > 0.9:
            actions.extend(["block", "log", "alert"])
        elif risk_score > 0.7:
            actions.extend(["log", "rate_limit", "monitor"])
        elif risk_score > 0.5:
            actions.extend(["log", "monitor"])

        return actions


class SecurityMonitor:
    """
    Security monitoring and metrics collection
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self.metrics_window = 3600  # 1 hour
        self.metrics_key = "security_metrics"

    async def record_request(self, assessment: Dict[str, Any]):
        """Record security metrics for a request"""
        metrics = await self._get_current_metrics()

        metrics.total_requests += 1

        if assessment.get('blocked'):
            metrics.blocked_requests += 1
        if assessment.get('suspicious'):
            metrics.suspicious_requests += 1
        if assessment.get('risk_score', 0) > 0.8:
            metrics.threats_detected += 1

        # Update average risk score
        current_avg = metrics.average_risk_score
        new_count = metrics.total_requests
        new_score = assessment.get('risk_score', 0)
        metrics.average_risk_score = (current_avg * (new_count - 1) + new_score) / new_count

        await self._save_metrics(metrics)

    async def get_metrics(self) -> SecurityMetrics:
        """Get current security metrics"""
        return await self._get_current_metrics()

    async def _get_current_metrics(self) -> SecurityMetrics:
        """Get current metrics from Redis"""
        data = await self.redis.get(self.metrics_key)
        if data:
            return SecurityMetrics(**json.loads(data))

        return SecurityMetrics()

    async def _save_metrics(self, metrics: SecurityMetrics):
        """Save metrics to Redis"""
        await self.redis.setex(
            self.metrics_key,
            self.metrics_window,
            json.dumps(metrics.__dict__)
        )


# Global instances
redis_client = Redis.from_url(settings.REDIS_URL)
rate_limiter = AdvancedRateLimiter(redis_client)
threat_detector = ThreatDetector(redis_client)
security_monitor = SecurityMonitor(redis_client)


async def check_security(request: Request) -> Dict[str, Any]:
    """
    Main security check function
    Returns security assessment
    """
    # Analyze for threats
    assessment = await threat_detector.analyze_request(request)

    # Record metrics
    await security_monitor.record_request(assessment)

    return assessment


async def get_security_metrics() -> SecurityMetrics:
    """Get current security metrics"""
    return await security_monitor.get_metrics()