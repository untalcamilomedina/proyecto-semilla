"""
Tests for Advanced Rate Limiting with ML
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.core.rate_limiter import AdaptiveRateLimiter, rate_limiter
from app.ml.rate_limiting.models import RequestClassifier, AbuseDetector
from app.ml.rate_limiting.features import FeatureExtractor
from app.services.rate_limit_service import RateLimitService


class TestAdaptiveRateLimiter:
    """Test cases for AdaptiveRateLimiter"""

    @pytest.fixture
    def rate_limiter_instance(self):
        """Create a fresh rate limiter instance for testing"""
        limiter = AdaptiveRateLimiter()
        # Clear any existing data
        limiter.request_cache.clear()
        limiter.whitelist.clear()
        limiter.blacklist.clear()
        return limiter

    def test_initialization(self, rate_limiter_instance):
        """Test rate limiter initialization"""
        assert rate_limiter_instance.classifier is not None
        assert rate_limiter_instance.abuse_detector is not None
        assert rate_limiter_instance.feature_extractor is not None
        assert isinstance(rate_limiter_instance.request_cache, dict)
        assert isinstance(rate_limiter_instance.whitelist, set)
        assert isinstance(rate_limiter_instance.blacklist, set)

    @pytest.mark.asyncio
    async def test_allow_normal_request(self, rate_limiter_instance):
        """Test allowing a normal request"""
        request_data = {
            'ip_address': '192.168.1.100',
            'method': 'GET',
            'path': '/api/v1/health',
            'user_agent': 'Mozilla/5.0 (compatible; Test/1.0)',
            'timestamp': datetime.utcnow()
        }

        result = await rate_limiter_instance.check_rate_limit(request_data)

        assert result['allowed'] is True
        assert result['reason'] in ['within_limits', 'no_redis']
        assert 'ip_address' in result

    @pytest.mark.asyncio
    async def test_whitelist_functionality(self, rate_limiter_instance):
        """Test whitelist functionality"""
        ip_address = '192.168.1.200'

        # Add to whitelist
        rate_limiter_instance.add_to_whitelist(ip_address)

        request_data = {
            'ip_address': ip_address,
            'method': 'GET',
            'path': '/api/v1/test',
            'user_agent': 'Test Agent',
            'timestamp': datetime.utcnow()
        }

        result = await rate_limiter_instance.check_rate_limit(request_data)

        assert result['allowed'] is True
        assert result['reason'] == 'whitelisted'

    @pytest.mark.asyncio
    async def test_blacklist_functionality(self, rate_limiter_instance):
        """Test blacklist functionality"""
        ip_address = '192.168.1.201'

        # Add to blacklist
        rate_limiter_instance.add_to_blacklist(ip_address)

        request_data = {
            'ip_address': ip_address,
            'method': 'GET',
            'path': '/api/v1/test',
            'user_agent': 'Test Agent',
            'timestamp': datetime.utcnow()
        }

        result = await rate_limiter_instance.check_rate_limit(request_data)

        assert result['allowed'] is False
        assert result['reason'] == 'blacklisted'

    def test_whitelist_blacklist_management(self, rate_limiter_instance):
        """Test whitelist/blacklist management functions"""
        ip1 = '192.168.1.100'
        ip2 = '192.168.1.101'

        # Test whitelist
        assert rate_limiter_instance.add_to_whitelist(ip1) is True
        assert ip1 in rate_limiter_instance.whitelist

        assert rate_limiter_instance.remove_from_whitelist(ip1) is True
        assert ip1 not in rate_limiter_instance.whitelist

        # Test blacklist
        assert rate_limiter_instance.add_to_blacklist(ip2) is True
        assert ip2 in rate_limiter_instance.blacklist

        assert rate_limiter_instance.remove_from_blacklist(ip2) is True
        assert ip2 not in rate_limiter_instance.blacklist

    def test_tenant_config_management(self, rate_limiter_instance):
        """Test tenant configuration management"""
        tenant_id = 'test-tenant-123'
        config = {
            'requests_per_minute': 100,
            'requests_per_hour': 2000,
            'burst_limit': 20,
            'adaptive_enabled': True,
            'ml_threshold': 0.8
        }

        rate_limiter_instance.update_tenant_config(tenant_id, config)

        assert tenant_id in rate_limiter_instance.tenant_configs
        assert rate_limiter_instance.tenant_configs[tenant_id]['requests_per_minute'] == 100

    def test_get_stats(self, rate_limiter_instance):
        """Test getting system statistics"""
        # Add some test data
        rate_limiter_instance.add_to_whitelist('192.168.1.100')
        rate_limiter_instance.add_to_blacklist('192.168.1.101')

        stats = rate_limiter_instance.get_stats()

        assert 'whitelist_count' in stats
        assert 'blacklist_count' in stats
        assert 'tenant_configs' in stats
        assert stats['whitelist_count'] == 1
        assert stats['blacklist_count'] == 1


class TestRequestClassifier:
    """Test cases for RequestClassifier"""

    @pytest.fixture
    def classifier(self):
        """Create a request classifier for testing"""
        return RequestClassifier()

    def test_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier.models is not None
        assert len(classifier.feature_names) > 0
        assert hasattr(classifier, 'scaler')

    def test_extract_features(self, classifier):
        """Test feature extraction"""
        request_data = {
            'request_count_per_minute': 10,
            'request_count_per_hour': 100,
            'unique_endpoints_count': 5,
            'avg_request_interval': 6.0,
            'burst_request_ratio': 0.1,
            'user_agent_entropy': 0.8,
            'ip_geographic_score': 0.7,
            'time_pattern_score': 0.6,
            'endpoint_diversity_score': 0.9
        }

        features = classifier.extract_features(request_data)

        assert features.shape == (1, 9)  # 9 features expected
        assert features.dtype == float

    def test_predict_normal_request(self, classifier):
        """Test prediction for normal request"""
        request_data = {
            'request_count_per_minute': 5,
            'request_count_per_hour': 50,
            'unique_endpoints_count': 3,
            'avg_request_interval': 12.0,
            'burst_request_ratio': 0.05,
            'user_agent_entropy': 0.9,
            'ip_geographic_score': 0.8,
            'time_pattern_score': 0.4,
            'endpoint_diversity_score': 0.8
        }

        prediction, confidence = classifier.predict(request_data)

        assert prediction in ['normal', 'suspicious']
        assert 0.0 <= confidence <= 1.0


class TestFeatureExtractor:
    """Test cases for FeatureExtractor"""

    @pytest.fixture
    def extractor(self):
        """Create a feature extractor for testing"""
        return FeatureExtractor()

    def test_initialization(self, extractor):
        """Test feature extractor initialization"""
        assert extractor.user_agents == set()
        assert extractor.endpoint_patterns == {}
        assert extractor.time_windows == {}

    def test_extract_basic_features(self, extractor):
        """Test basic feature extraction"""
        request_data = {
            'method': 'POST',
            'path': '/api/v1/users',
            'user_agent': 'Test Agent',
            'ip_address': '192.168.1.100',
            'content_length': 1024,
            'query_params': {'page': '1'},
            'headers': {'content-type': 'application/json'}
        }

        features = extractor.extract_request_features(request_data)

        assert 'method' in features
        assert 'path' in features
        assert 'user_agent' in features
        assert 'ip_address' in features
        assert features['method'] == 'POST'
        assert features['path'] == '/api/v1/users'

    def test_extract_temporal_features(self, extractor):
        """Test temporal feature extraction"""
        current_time = datetime.utcnow()
        historical_requests = [
            {
                'ip_address': '192.168.1.100',
                'timestamp': current_time - timedelta(minutes=5),
                'path': '/api/v1/test1'
            },
            {
                'ip_address': '192.168.1.100',
                'timestamp': current_time - timedelta(minutes=3),
                'path': '/api/v1/test2'
            }
        ]

        request_data = {
            'ip_address': '192.168.1.100',
            'timestamp': current_time,
            'path': '/api/v1/test3'
        }

        features = extractor.extract_request_features(request_data, historical_requests)

        assert 'request_count_per_minute' in features
        assert 'request_count_per_5_minutes' in features
        assert 'avg_request_interval' in features
        assert features['request_count_per_minute'] >= 0


class TestRateLimitService:
    """Test cases for RateLimitService"""

    @pytest.fixture
    def service(self):
        """Create a rate limit service for testing"""
        return RateLimitService()

    @pytest.mark.asyncio
    async def test_get_rate_limit_status(self, service):
        """Test getting rate limit status"""
        # Mock the rate limiter
        with patch('app.services.rate_limit_service.rate_limiter') as mock_limiter:
            mock_limiter.get_rate_limit_status = AsyncMock(return_value={
                'ip_address': '192.168.1.100',
                'current_counts': {'ip_minute': 5},
                'limits': {'requests_per_minute': 60},
                'risk_score': 0.1
            })

            result = await service.get_rate_limit_status(
                ip_address='192.168.1.100',
                tenant_id='test-tenant'
            )

            assert 'ip_address' in result
            assert 'current_counts' in result
            assert 'limits' in result

    def test_validate_tenant_config(self, service):
        """Test tenant configuration validation"""
        # Valid config
        valid_config = {
            'requests_per_minute': 100,
            'requests_per_hour': 1000,
            'burst_limit': 10,
            'adaptive_enabled': True,
            'ml_threshold': 0.7,
            'block_duration_minutes': 15
        }

        result = service._validate_tenant_config(valid_config)
        assert result['valid'] is True
        assert len(result['errors']) == 0

        # Invalid config
        invalid_config = {
            'requests_per_minute': -1,  # Invalid
            'requests_per_hour': 1000,
            'burst_limit': 10,
            'adaptive_enabled': True,
            'ml_threshold': 0.7,
            'block_duration_minutes': 15
        }

        result = service._validate_tenant_config(invalid_config)
        assert result['valid'] is False
        assert len(result['errors']) > 0


# Integration tests
class TestRateLimitingIntegration:
    """Integration tests for the complete rate limiting system"""

    @pytest.mark.asyncio
    async def test_full_request_flow(self):
        """Test complete request flow through rate limiting"""
        # This would test the full integration with middleware
        # For now, just test the core components work together
        limiter = AdaptiveRateLimiter()

        # Simulate a series of requests
        base_request = {
            'ip_address': '192.168.1.100',
            'method': 'GET',
            'path': '/api/v1/test',
            'user_agent': 'Test Agent',
            'timestamp': datetime.utcnow()
        }

        # First request should be allowed
        result1 = await limiter.check_rate_limit(base_request)
        assert result1['allowed'] is True

        # Second request should also be allowed (within limits)
        result2 = await limiter.check_rate_limit(base_request)
        assert result2['allowed'] is True

        # Check that request was tracked
        assert base_request['ip_address'] in limiter.request_cache
        assert len(limiter.request_cache[base_request['ip_address']]) >= 2

    def test_ml_model_integration(self):
        """Test ML model integration"""
        classifier = RequestClassifier()
        detector = AbuseDetector()
        extractor = FeatureExtractor()

        # Test that all components can work together
        request_data = {
            'ip_address': '192.168.1.100',
            'method': 'GET',
            'path': '/api/v1/test',
            'user_agent': 'Test Agent',
            'timestamp': datetime.utcnow()
        }

        # Extract features
        features = extractor.extract_request_features(request_data)

        # Classify request
        prediction, confidence = classifier.predict(features)

        # Check for anomalies
        pattern = {
            'total_requests': 10,
            'unique_ips': 1,
            'time_span_minutes': 5,
            'burst_events': 0
        }

        is_anomaly, score = detector.detect_anomaly(pattern)

        # All should return valid results
        assert prediction in ['normal', 'suspicious']
        assert 0.0 <= confidence <= 1.0
        assert isinstance(is_anomaly, bool)
        assert 0.0 <= score <= 1.0