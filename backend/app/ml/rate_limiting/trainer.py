"""
Model training utilities for ML-based rate limiting
Handles training, validation, and model updates
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

from .models import RequestClassifier, AbuseDetector
from .features import FeatureExtractor

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Handles training and updating of ML models for rate limiting
    Manages data collection, preprocessing, and model retraining
    """

    def __init__(self, data_path: Optional[str] = None, models_path: Optional[str] = None):
        self.data_path = data_path or "backend/app/ml/rate_limiting/data"
        self.models_path = models_path or "backend/app/ml/rate_limiting/models"
        self.feature_extractor = FeatureExtractor()
        self.classifier = RequestClassifier()
        self.abuse_detector = AbuseDetector()

        # Ensure directories exist
        Path(self.data_path).mkdir(parents=True, exist_ok=True)
        Path(self.models_path).mkdir(parents=True, exist_ok=True)

    def collect_training_data(self, historical_requests: List[Dict[str, Any]],
                            labels: Optional[List[int]] = None) -> Tuple[List[Dict[str, Any]], List[int]]:
        """
        Collect and preprocess training data from historical requests

        Args:
            historical_requests: List of historical request data
            labels: Optional labels for supervised learning (0=normal, 1=suspicious)

        Returns:
            Tuple of (processed_data, labels)
        """
        processed_data = []
        training_labels = labels or []

        logger.info(f"Processing {len(historical_requests)} historical requests for training")

        # Group requests by IP for feature extraction
        ip_groups = self._group_requests_by_ip(historical_requests)

        for ip_address, requests in ip_groups.items():
            if len(requests) < 3:  # Skip IPs with too few requests
                continue

            # Extract features for each request in context
            for i, request in enumerate(requests):
                # Use previous requests as context
                context_requests = requests[:i] if i > 0 else []

                features = self.feature_extractor.extract_request_features(
                    request, context_requests
                )

                processed_data.append(features)

                # Generate labels if not provided
                if not labels:
                    label = self._generate_label(request, context_requests)
                    training_labels.append(label)

        logger.info(f"Generated {len(processed_data)} training samples")
        return processed_data, training_labels

    def train_classifier(self, training_data: List[Dict[str, Any]],
                        labels: List[int], test_size: float = 0.2) -> Dict[str, Any]:
        """
        Train the request classifier model

        Args:
            training_data: Processed training data
            labels: Training labels
            test_size: Fraction of data to use for testing

        Returns:
            Training results and metrics
        """
        logger.info("Starting classifier training...")

        try:
            self.classifier.train(training_data, labels)

            # Evaluate model
            results = self._evaluate_classifier(training_data, labels, test_size)

            logger.info("Classifier training completed successfully")
            return results

        except Exception as e:
            logger.error(f"Classifier training failed: {e}")
            return {"error": str(e)}

    def train_abuse_detector(self, normal_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the abuse detector with normal patterns

        Args:
            normal_patterns: List of normal request patterns

        Returns:
            Training results
        """
        logger.info("Starting abuse detector training...")

        try:
            self.abuse_detector.train(normal_patterns)

            logger.info("Abuse detector training completed successfully")
            return {"status": "success", "samples": len(normal_patterns)}

        except Exception as e:
            logger.error(f"Abuse detector training failed: {e}")
            return {"error": str(e)}

    def update_models(self, new_requests: List[Dict[str, Any]],
                     force_retrain: bool = False) -> Dict[str, Any]:
        """
        Update models with new request data
        Performs incremental learning or full retraining as needed

        Args:
            new_requests: New request data for model update
            force_retrain: Force full retraining instead of incremental

        Returns:
            Update results
        """
        results = {"timestamp": datetime.utcnow().isoformat()}

        # Check if retraining is needed
        if force_retrain or self._should_retrain():
            logger.info("Performing full model retraining")

            # Load historical data
            historical_data = self._load_historical_data()

            # Combine with new data
            all_data = historical_data + new_requests

            # Train classifier
            training_data, labels = self.collect_training_data(all_data)
            if training_data:
                classifier_results = self.train_classifier(training_data, labels)
                results["classifier"] = classifier_results

            # Train abuse detector with normal patterns
            normal_patterns = self._extract_normal_patterns(all_data)
            if normal_patterns:
                abuse_results = self.train_abuse_detector(normal_patterns)
                results["abuse_detector"] = abuse_results

            # Save updated historical data
            self._save_historical_data(all_data)

        else:
            logger.info("Models are up to date, skipping retraining")

        return results

    def _group_requests_by_ip(self, requests: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group requests by IP address"""
        ip_groups = {}

        for request in requests:
            ip = request.get('ip_address', 'unknown')
            if ip not in ip_groups:
                ip_groups[ip] = []
            ip_groups[ip].append(request)

        return ip_groups

    def _generate_label(self, request: Dict[str, Any],
                       context_requests: List[Dict[str, Any]]) -> int:
        """
        Generate training label based on request patterns
        Uses heuristic rules to identify suspicious behavior
        """
        # Extract features for labeling
        features = self.feature_extractor.extract_request_features(request, context_requests)

        # Heuristic rules for suspicious behavior
        suspicious_score = 0

        # High request frequency
        if features.get('request_count_per_minute', 0) > 30:
            suspicious_score += 0.3
        if features.get('request_count_per_hour', 0) > 500:
            suspicious_score += 0.3

        # Burst patterns
        if features.get('burst_request_ratio', 0) > 0.7:
            suspicious_score += 0.2

        # Low endpoint diversity
        if features.get('endpoint_diversity_score', 0.5) < 0.3:
            suspicious_score += 0.2

        # High failed request ratio
        if features.get('failed_requests_ratio', 0) > 0.5:
            suspicious_score += 0.2

        # Suspicious user agent
        if features.get('user_agent_suspicious_score', 0) > 0.5:
            suspicious_score += 0.2

        # API enumeration patterns
        if features.get('api_enumeration_score', 0) > 0.3:
            suspicious_score += 0.2

        # Regular timing patterns (robotic behavior)
        if features.get('time_pattern_score', 0.5) > 0.7:
            suspicious_score += 0.2

        # Return 1 (suspicious) if score exceeds threshold
        return 1 if suspicious_score > 0.5 else 0

    def _evaluate_classifier(self, training_data: List[Dict[str, Any]],
                           labels: List[int], test_size: float) -> Dict[str, Any]:
        """Evaluate classifier performance"""
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, confusion_matrix

        # This is a simplified evaluation - in practice you'd want more sophisticated metrics
        total_samples = len(training_data)
        positive_samples = sum(labels)
        negative_samples = total_samples - positive_samples

        return {
            "total_samples": total_samples,
            "positive_samples": positive_samples,
            "negative_samples": negative_samples,
            "positive_ratio": positive_samples / total_samples if total_samples > 0 else 0
        }

    def _should_retrain(self) -> bool:
        """Determine if models should be retrained"""
        # Check if enough new data has been collected
        # Check model performance degradation
        # Check time since last training

        # For now, simple time-based check (retrain weekly)
        model_file = Path(self.classifier.model_path)
        if not model_file.exists():
            return True

        last_modified = datetime.fromtimestamp(model_file.stat().st_mtime)
        days_since_training = (datetime.utcnow() - last_modified).days

        return days_since_training > 7

    def _load_historical_data(self) -> List[Dict[str, Any]]:
        """Load historical training data"""
        data_file = Path(self.data_path) / "historical_requests.json"

        if not data_file.exists():
            return []

        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} historical requests")
            return data
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return []

    def _save_historical_data(self, data: List[Dict[str, Any]]):
        """Save historical training data"""
        data_file = Path(self.data_path) / "historical_requests.json"

        try:
            # Keep only recent data (last 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            recent_data = [
                req for req in data
                if datetime.fromisoformat(req.get('timestamp', '2000-01-01T00:00:00')) > cutoff_date
            ]

            with open(data_file, 'w') as f:
                json.dump(recent_data, f, indent=2, default=str)

            logger.info(f"Saved {len(recent_data)} historical requests")

        except Exception as e:
            logger.error(f"Failed to save historical data: {e}")

    def _extract_normal_patterns(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract patterns from normal (non-suspicious) requests"""
        normal_patterns = []

        # Group by IP and analyze patterns
        ip_groups = self._group_requests_by_ip(requests)

        for ip_address, ip_requests in ip_groups.items():
            if len(ip_requests) < 5:  # Skip IPs with too few requests
                continue

            # Calculate pattern metrics for this IP
            pattern = {
                'ip_address': ip_address,
                'total_requests': len(ip_requests),
                'unique_endpoints': len(set(req.get('path', '/') for req in ip_requests)),
                'time_span_minutes': self._calculate_time_span(ip_requests),
                'avg_requests_per_minute': len(ip_requests) / max(self._calculate_time_span(ip_requests), 1),
                'endpoint_diversity': len(set(req.get('path', '/') for req in ip_requests)) / len(ip_requests),
                'method_diversity': len(set(req.get('method', 'GET') for req in ip_requests))
            }

            # Only include patterns that seem normal
            if (pattern['avg_requests_per_minute'] < 10 and  # Not too frequent
                pattern['endpoint_diversity'] > 0.2):       # Some endpoint diversity
                normal_patterns.append(pattern)

        return normal_patterns

    def _calculate_time_span(self, requests: List[Dict[str, Any]]) -> float:
        """Calculate time span of requests in minutes"""
        if not requests:
            return 0

        timestamps = [datetime.fromisoformat(req.get('timestamp', '2000-01-01T00:00:00'))
                     for req in requests if req.get('timestamp')]

        if not timestamps:
            return 0

        time_span = max(timestamps) - min(timestamps)
        return time_span.total_seconds() / 60  # Convert to minutes

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about current models"""
        return {
            "classifier": {
                "model_path": self.classifier.model_path,
                "models_loaded": len(self.classifier.models) > 0
            },
            "abuse_detector": {
                "model_path": self.abuse_detector.model_path,
                "model_loaded": self.abuse_detector.model is not None
            },
            "data_path": self.data_path,
            "models_path": self.models_path
        }