"""
Machine Learning models for advanced rate limiting
Implements classification algorithms for request analysis and abuse detection
"""

import pickle
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

logger = logging.getLogger(__name__)


class RequestClassifier:
    """
    ML classifier for categorizing HTTP requests as normal or suspicious
    Uses multiple algorithms (Random Forest, SVM) with ensemble voting
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "backend/app/ml/rate_limiting/models/request_classifier.pkl"
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = [
            'request_count_per_minute',
            'request_count_per_hour',
            'unique_endpoints_count',
            'avg_request_interval',
            'burst_request_ratio',
            'user_agent_entropy',
            'ip_geographic_score',
            'time_pattern_score',
            'endpoint_diversity_score'
        ]
        self._load_or_create_models()

    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        model_file = Path(self.model_path)
        if model_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    self.models = pickle.load(f)
                logger.info("Loaded existing request classifier models")
            except Exception as e:
                logger.warning(f"Failed to load models: {e}, creating new ones")
                self._create_models()
        else:
            self._create_models()

    def _create_models(self):
        """Create new ML models"""
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            ),
            'svm': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                class_weight='balanced',
                random_state=42
            )
        }
        logger.info("Created new request classifier models")

    def extract_features(self, request_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from request data for ML classification

        Args:
            request_data: Dictionary containing request metrics

        Returns:
            Feature vector as numpy array
        """
        features = []

        # Request frequency features
        features.append(request_data.get('request_count_per_minute', 0))
        features.append(request_data.get('request_count_per_hour', 0))

        # Endpoint diversity
        features.append(request_data.get('unique_endpoints_count', 1))

        # Timing patterns
        features.append(request_data.get('avg_request_interval', 60.0))

        # Burst detection
        features.append(request_data.get('burst_request_ratio', 0.0))

        # User agent analysis
        features.append(request_data.get('user_agent_entropy', 0.0))

        # Geographic scoring
        features.append(request_data.get('ip_geographic_score', 0.5))

        # Time pattern analysis
        features.append(request_data.get('time_pattern_score', 0.5))

        # Endpoint diversity score
        features.append(request_data.get('endpoint_diversity_score', 0.5))

        return np.array(features).reshape(1, -1)

    def predict(self, request_data: Dict[str, Any]) -> Tuple[str, float]:
        """
        Predict if request is normal or suspicious

        Args:
            request_data: Request metrics and features

        Returns:
            Tuple of (prediction, confidence_score)
        """
        if not self.models:
            return "normal", 0.5

        try:
            features = self.extract_features(request_data)
            features_scaled = self.scaler.transform(features)

            predictions = []
            probabilities = []

            # Get predictions from all models
            for name, model in self.models.items():
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features_scaled)[0]
                    pred = model.predict(features_scaled)[0]
                    predictions.append(pred)
                    probabilities.append(max(proba))
                else:
                    pred = model.predict(features_scaled)[0]
                    predictions.append(pred)
                    probabilities.append(0.5)

            # Ensemble voting
            normal_count = sum(1 for p in predictions if p == 0)
            suspicious_count = sum(1 for p in predictions if p == 1)

            if suspicious_count > normal_count:
                prediction = "suspicious"
            else:
                prediction = "normal"

            confidence = np.mean(probabilities)

            return prediction, float(confidence)

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return "normal", 0.5

    def train(self, training_data: List[Dict[str, Any]], labels: List[int]):
        """
        Train the ML models with historical data

        Args:
            training_data: List of request data dictionaries
            labels: List of labels (0=normal, 1=suspicious)
        """
        try:
            # Extract features from training data
            X = []
            for data in training_data:
                features = self.extract_features(data)
                X.append(features.flatten())

            X = np.array(X)
            y = np.array(labels)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train models
            for name, model in self.models.items():
                model.fit(X_train_scaled, y_train)

                # Evaluate
                y_pred = model.predict(X_test_scaled)
                logger.info(f"{name} Classification Report:")
                logger.info(classification_report(y_test, y_pred))

            # Save trained models
            self._save_models()

        except Exception as e:
            logger.error(f"Training error: {e}")

    def _save_models(self):
        """Save trained models to disk"""
        try:
            Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.models, f)
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Failed to save models: {e}")


class AbuseDetector:
    """
    Anomaly detection for identifying abusive patterns
    Uses Isolation Forest for unsupervised anomaly detection
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "backend/app/ml/rate_limiting/models/abuse_detector.pkl"
        self.model = None
        self.scaler = StandardScaler()
        self.contamination = 0.1  # Expected percentage of anomalies
        self._load_or_create_model()

    def _load_or_create_model(self):
        """Load existing model or create new one"""
        model_file = Path(self.model_path)
        if model_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Loaded existing abuse detector model")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}, creating new one")
                self._create_model()
        else:
            self._create_model()

    def _create_model(self):
        """Create new Isolation Forest model"""
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        logger.info("Created new abuse detector model")

    def detect_anomaly(self, request_pattern: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Detect if request pattern is anomalous

        Args:
            request_pattern: Dictionary containing pattern metrics

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if not self.model:
            return False, 0.0

        try:
            # Extract pattern features
            features = self._extract_pattern_features(request_pattern)
            features_scaled = self.scaler.transform(features.reshape(1, -1))

            # Get anomaly score
            score = self.model.decision_function(features_scaled)[0]
            prediction = self.model.predict(features_scaled)[0]

            # Convert to boolean (1 = normal, -1 = anomaly)
            is_anomaly = prediction == -1

            # Convert score to 0-1 range (higher = more anomalous)
            anomaly_score = (score + 1) / 2

            return is_anomaly, float(anomaly_score)

        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return False, 0.0

    def _extract_pattern_features(self, pattern: Dict[str, Any]) -> np.ndarray:
        """Extract features from request pattern for anomaly detection"""
        features = [
            pattern.get('total_requests', 0),
            pattern.get('unique_ips', 1),
            pattern.get('avg_requests_per_ip', 0),
            pattern.get('time_span_minutes', 1),
            pattern.get('burst_events', 0),
            pattern.get('failed_requests_ratio', 0),
            pattern.get('endpoint_concentration', 0),
            pattern.get('geographic_spread', 0)
        ]
        return np.array(features)

    def train(self, normal_patterns: List[Dict[str, Any]]):
        """
        Train the anomaly detector with normal patterns

        Args:
            normal_patterns: List of normal request patterns
        """
        try:
            # Extract features from normal patterns
            X = []
            for pattern in normal_patterns:
                features = self._extract_pattern_features(pattern)
                X.append(features)

            X = np.array(X)

            # Fit scaler and model
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)

            # Save trained model
            self._save_model()

            logger.info("Abuse detector trained successfully")

        except Exception as e:
            logger.error(f"Training error: {e}")

    def _save_model(self):
        """Save trained model to disk"""
        try:
            Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info("Abuse detector model saved successfully")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")