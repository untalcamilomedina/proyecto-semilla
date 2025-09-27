"""
Feature extraction for ML-based rate limiting
Extracts and computes features from HTTP requests for abuse detection
"""

import math
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import logging
import re

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extracts features from HTTP requests for ML analysis
    Computes various metrics for abuse detection and classification
    """

    def __init__(self):
        self.user_agents = set()
        self.endpoint_patterns = {}
        self.time_windows = {}

    def extract_request_features(self, request_data: Dict[str, Any],
                               historical_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Extract comprehensive features from a single request

        Args:
            request_data: Current request data
            historical_data: List of historical requests for context

        Returns:
            Dictionary of extracted features
        """
        features = {}

        # Basic request features
        features.update(self._extract_basic_features(request_data))

        # Temporal features
        features.update(self._extract_temporal_features(request_data, historical_data or []))

        # Behavioral features
        features.update(self._extract_behavioral_features(request_data, historical_data or []))

        # Geographic features (placeholder for IP geolocation)
        features.update(self._extract_geographic_features(request_data))

        # User agent analysis
        features.update(self._extract_user_agent_features(request_data))

        # Endpoint analysis
        features.update(self._extract_endpoint_features(request_data, historical_data or []))

        return features

    def _extract_basic_features(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic request features"""
        return {
            'method': request_data.get('method', 'GET'),
            'path': request_data.get('path', '/'),
            'user_agent': request_data.get('user_agent', ''),
            'ip_address': request_data.get('ip_address', 'unknown'),
            'content_length': request_data.get('content_length', 0),
            'query_params_count': len(request_data.get('query_params', {})),
            'headers_count': len(request_data.get('headers', {}))
        }

    def _extract_temporal_features(self, request_data: Dict[str, Any],
                                 historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract time-based features"""
        current_time = request_data.get('timestamp', datetime.utcnow())
        ip_address = request_data.get('ip_address', 'unknown')

        # Calculate request frequency in different time windows
        request_count_1min = self._count_requests_in_window(
            historical_data, ip_address, current_time, timedelta(minutes=1)
        )
        request_count_5min = self._count_requests_in_window(
            historical_data, ip_address, current_time, timedelta(minutes=5)
        )
        request_count_1hour = self._count_requests_in_window(
            historical_data, ip_address, current_time, timedelta(hours=1)
        )

        # Calculate average interval between requests
        avg_interval = self._calculate_avg_request_interval(historical_data, ip_address, current_time)

        # Detect burst patterns
        burst_ratio = self._calculate_burst_ratio(historical_data, ip_address, current_time)

        # Time pattern analysis
        time_pattern_score = self._analyze_time_pattern(historical_data, ip_address, current_time)

        return {
            'request_count_per_minute': request_count_1min,
            'request_count_per_5_minutes': request_count_5min,
            'request_count_per_hour': request_count_1hour,
            'avg_request_interval': avg_interval,
            'burst_request_ratio': burst_ratio,
            'time_pattern_score': time_pattern_score
        }

    def _extract_behavioral_features(self, request_data: Dict[str, Any],
                                   historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract behavioral patterns"""
        ip_address = request_data.get('ip_address', 'unknown')
        current_path = request_data.get('path', '/')

        # Endpoint diversity
        unique_endpoints = set()
        for req in historical_data:
            if req.get('ip_address') == ip_address:
                unique_endpoints.add(req.get('path', '/'))

        # Calculate endpoint concentration
        endpoint_counts = Counter(req.get('path', '/') for req in historical_data
                                if req.get('ip_address') == ip_address)
        total_requests = len([req for req in historical_data
                            if req.get('ip_address') == ip_address])

        if total_requests > 0:
            most_common_endpoint_count = endpoint_counts.most_common(1)[0][1] if endpoint_counts else 0
            endpoint_concentration = most_common_endpoint_count / total_requests
        else:
            endpoint_concentration = 0

        # Request method diversity
        method_diversity = len(set(req.get('method', 'GET') for req in historical_data
                                 if req.get('ip_address') == ip_address))

        # Failed request ratio (assuming status codes >= 400 are failures)
        failed_requests = len([req for req in historical_data
                             if req.get('ip_address') == ip_address and
                             req.get('status_code', 200) >= 400])
        total_ip_requests = len([req for req in historical_data
                               if req.get('ip_address') == ip_address])
        failed_ratio = failed_requests / total_ip_requests if total_ip_requests > 0 else 0

        return {
            'unique_endpoints_count': len(unique_endpoints),
            'endpoint_concentration': endpoint_concentration,
            'method_diversity': method_diversity,
            'failed_requests_ratio': failed_ratio,
            'endpoint_diversity_score': 1.0 / (1.0 + endpoint_concentration)  # Lower concentration = higher diversity
        }

    def _extract_geographic_features(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract geographic features from IP address"""
        ip_address = request_data.get('ip_address', 'unknown')

        # Placeholder for IP geolocation service
        # In production, integrate with services like MaxMind GeoIP
        geographic_score = self._calculate_geographic_score(ip_address)

        return {
            'ip_geographic_score': geographic_score,
            'is_vpn_proxy': self._detect_vpn_proxy(ip_address)
        }

    def _extract_user_agent_features(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from User-Agent string"""
        user_agent = request_data.get('user_agent', '')

        # Calculate entropy of user agent
        entropy = self._calculate_string_entropy(user_agent)

        # Detect suspicious patterns
        suspicious_patterns = [
            r'bot|crawler|spider|scraper',
            r'python|curl|wget|postman',
            r'headless|selenium|phantom',
            r'unknown|undefined|null'
        ]

        suspicious_score = 0
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                suspicious_score += 0.2

        return {
            'user_agent_entropy': entropy,
            'user_agent_suspicious_score': min(suspicious_score, 1.0),
            'user_agent_length': len(user_agent)
        }

    def _extract_endpoint_features(self, request_data: Dict[str, Any],
                                 historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract features related to API endpoints"""
        current_path = request_data.get('path', '/')
        ip_address = request_data.get('ip_address', 'unknown')

        # Analyze endpoint access patterns
        endpoint_access_pattern = self._analyze_endpoint_pattern(current_path, historical_data, ip_address)

        # Detect API enumeration attempts
        enumeration_score = self._detect_api_enumeration(historical_data, ip_address)

        return {
            'endpoint_access_pattern': endpoint_access_pattern,
            'api_enumeration_score': enumeration_score
        }

    def _count_requests_in_window(self, historical_data: List[Dict[str, Any]],
                                ip_address: str, current_time: datetime,
                                time_window: timedelta) -> int:
        """Count requests from IP in given time window"""
        window_start = current_time - time_window
        count = 0

        for req in historical_data:
            if (req.get('ip_address') == ip_address and
                req.get('timestamp', datetime.min) >= window_start and
                req.get('timestamp', datetime.min) <= current_time):
                count += 1

        return count

    def _calculate_avg_request_interval(self, historical_data: List[Dict[str, Any]],
                                      ip_address: str, current_time: datetime) -> float:
        """Calculate average time interval between requests"""
        ip_requests = [req for req in historical_data
                      if req.get('ip_address') == ip_address]

        if len(ip_requests) < 2:
            return 60.0  # Default 1 minute

        # Sort by timestamp
        sorted_requests = sorted(ip_requests, key=lambda x: x.get('timestamp', datetime.min))

        intervals = []
        for i in range(1, len(sorted_requests)):
            interval = (sorted_requests[i]['timestamp'] - sorted_requests[i-1]['timestamp']).total_seconds()
            if interval > 0:
                intervals.append(interval)

        return sum(intervals) / len(intervals) if intervals else 60.0

    def _calculate_burst_ratio(self, historical_data: List[Dict[str, Any]],
                             ip_address: str, current_time: datetime) -> float:
        """Calculate ratio of requests in short burst vs normal pattern"""
        # Count requests in last 10 seconds vs last minute
        burst_window = timedelta(seconds=10)
        normal_window = timedelta(minutes=1)

        burst_count = self._count_requests_in_window(historical_data, ip_address, current_time, burst_window)
        normal_count = self._count_requests_in_window(historical_data, ip_address, current_time, normal_window)

        if normal_count == 0:
            return 0.0

        return burst_count / normal_count

    def _analyze_time_pattern(self, historical_data: List[Dict[str, Any]],
                            ip_address: str, current_time: datetime) -> float:
        """Analyze if request timing follows suspicious patterns"""
        ip_requests = [req for req in historical_data
                      if req.get('ip_address') == ip_address]

        if len(ip_requests) < 5:
            return 0.5  # Neutral score

        # Check for perfectly regular intervals (suspicious)
        intervals = []
        sorted_requests = sorted(ip_requests, key=lambda x: x.get('timestamp', datetime.min))

        for i in range(1, len(sorted_requests)):
            interval = (sorted_requests[i]['timestamp'] - sorted_requests[i-1]['timestamp']).total_seconds()
            intervals.append(interval)

        if not intervals:
            return 0.5

        # Calculate coefficient of variation
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = math.sqrt(variance)

        if mean_interval == 0:
            return 1.0  # Highly suspicious

        cv = std_dev / mean_interval  # Coefficient of variation

        # Very low CV indicates robotic behavior
        if cv < 0.1:
            return 0.9  # Very suspicious
        elif cv < 0.3:
            return 0.7  # Moderately suspicious
        else:
            return 0.3  # Normal variation

    def _calculate_geographic_score(self, ip_address: str) -> float:
        """Calculate geographic risk score for IP address"""
        # Placeholder implementation
        # In production, use GeoIP database
        if ip_address == 'unknown':
            return 0.5

        # Simple heuristics based on IP patterns
        if ip_address.startswith(('10.', '192.168.', '172.')):
            return 0.1  # Private IP, low risk
        elif ip_address.startswith(('127.', 'localhost')):
            return 0.0  # Localhost, no risk

        return 0.5  # Default neutral score

    def _detect_vpn_proxy(self, ip_address: str) -> bool:
        """Detect if IP is likely from VPN or proxy"""
        # Placeholder implementation
        # In production, use VPN detection services
        return False

    def _calculate_string_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not text:
            return 0.0

        char_counts = Counter(text)
        length = len(text)
        entropy = 0

        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def _analyze_endpoint_pattern(self, current_path: str,
                                historical_data: List[Dict[str, Any]],
                                ip_address: str) -> float:
        """Analyze endpoint access pattern"""
        ip_requests = [req for req in historical_data
                      if req.get('ip_address') == ip_address]

        if not ip_requests:
            return 0.5

        # Check if current endpoint is frequently accessed
        endpoint_counts = Counter(req.get('path', '/') for req in ip_requests)
        current_count = endpoint_counts.get(current_path, 0)
        total_requests = len(ip_requests)

        frequency = current_count / total_requests

        # High frequency of same endpoint might be suspicious
        if frequency > 0.8:
            return 0.8  # Very suspicious
        elif frequency > 0.5:
            return 0.6  # Moderately suspicious
        else:
            return 0.3  # Normal

    def _detect_api_enumeration(self, historical_data: List[Dict[str, Any]],
                              ip_address: str) -> float:
        """Detect API enumeration attempts"""
        ip_requests = [req for req in historical_data
                      if req.get('ip_address') == ip_address]

        if len(ip_requests) < 10:
            return 0.0

        # Look for patterns typical of API enumeration
        paths = [req.get('path', '/') for req in ip_requests]

        # Check for sequential ID patterns
        sequential_patterns = 0
        for i in range(len(paths) - 1):
            if self._are_paths_sequential(paths[i], paths[i + 1]):
                sequential_patterns += 1

        enumeration_score = sequential_patterns / len(paths)

        return min(enumeration_score, 1.0)

    def _are_paths_sequential(self, path1: str, path2: str) -> bool:
        """Check if two paths appear to be sequential (e.g., /users/1, /users/2)"""
        # Simple heuristic for sequential patterns
        import re

        # Extract numbers from paths
        num1 = re.findall(r'\d+', path1)
        num2 = re.findall(r'\d+', path2)

        if not num1 or not num2:
            return False

        # Check if numbers are consecutive
        try:
            return abs(int(num1[-1]) - int(num2[-1])) == 1
        except ValueError:
            return False