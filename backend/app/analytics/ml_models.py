"""
Machine Learning Models for Analytics Predictions
Advanced ML models for user behavior prediction and anomaly detection
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics
import math
import random
from collections import defaultdict

from .models import PredictionResult, PredictionModel, MetricData

@dataclass
class MLModelConfig:
    """Configuration for ML models"""
    model_type: PredictionModel
    parameters: Dict[str, Any]
    training_window: int = 7200  # 2 hours
    prediction_horizon: int = 3600  # 1 hour
    min_data_points: int = 10
    confidence_threshold: float = 0.7

class MLModelRegistry:
    """Registry for ML models"""

    def __init__(self):
        self.models: Dict[str, 'BaseMLModel'] = {}
        self._register_builtin_models()

    def _register_builtin_models(self):
        """Register built-in ML models"""
        self.register_model(SimpleLinearRegression())
        self.register_model(MovingAveragePredictor())
        self.register_model(ExponentialSmoothing())
        self.register_model(SimpleAnomalyDetector())
        self.register_model(TrendAnalyzer())

    def register_model(self, model: 'BaseMLModel'):
        """Register a new ML model"""
        self.models[model.model_type.value] = model

    def get_model(self, model_type: PredictionModel) -> Optional['BaseMLModel']:
        """Get ML model by type"""
        return self.models.get(model_type.value)

class BaseMLModel:
    """Base class for ML models"""

    def __init__(self, model_type: PredictionModel):
        self.model_type = model_type
        self.is_trained = False
        self.last_trained: Optional[datetime] = None
        self.accuracy_score: float = 0.0

    async def train(self, data: List[MetricData]) -> bool:
        """Train the model with historical data"""
        raise NotImplementedError

    async def predict(self, data: List[MetricData], horizon: int = 3600) -> Optional[Dict[str, Any]]:
        """Make prediction using trained model"""
        raise NotImplementedError

    def _validate_data(self, data: List[MetricData], min_points: int = 10) -> bool:
        """Validate input data"""
        if len(data) < min_points:
            return False

        # Check for valid values
        values = [d.value for d in data]
        if not all(isinstance(v, (int, float)) and not math.isnan(v) for v in values):
            return False

        return True

    def _calculate_confidence(self, predictions: List[float], actuals: List[float]) -> float:
        """Calculate prediction confidence"""
        if len(predictions) != len(actuals) or len(actuals) == 0:
            return 0.0

        # Mean Absolute Percentage Error
        mape = np.mean([
            abs((actual - pred) / max(actual, 0.01))
            for actual, pred in zip(actuals, predictions)
        ])

        # Convert MAPE to confidence score (lower MAPE = higher confidence)
        confidence = max(0.0, min(1.0, 1.0 - mape))

        return confidence

class SimpleLinearRegression(BaseMLModel):
    """Simple linear regression for trend prediction"""

    def __init__(self):
        super().__init__(PredictionModel.LINEAR_REGRESSION)

    async def train(self, data: List[MetricData]) -> bool:
        """Train linear regression model"""
        if not self._validate_data(data, 5):
            return False

        # Simple linear regression implementation
        values = [d.value for d in data]
        n = len(values)

        # Calculate trend
        x = list(range(n))
        y = values

        # Simple linear regression
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return False

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        self.slope = slope
        self.intercept = intercept
        self.is_trained = True
        self.last_trained = datetime.utcnow()

        # Calculate accuracy on training data
        predictions = [slope * xi + intercept for xi in x]
        self.accuracy_score = self._calculate_confidence(predictions, y)

        return True

    async def predict(self, data: List[MetricData], horizon: int = 3600) -> Optional[Dict[str, Any]]:
        """Make linear regression prediction"""
        if not self.is_trained or not data:
            return None

        # Predict next value
        next_x = len(data)
        prediction = self.slope * next_x + self.intercept

        # Calculate trend direction
        trend = "increasing" if self.slope > 0 else "decreasing" if self.slope < 0 else "stable"

        return {
            "value": max(0, prediction),
            "confidence": self.accuracy_score,
            "trend": trend,
            "slope": self.slope,
            "method": "linear_regression"
        }

class MovingAveragePredictor(BaseMLModel):
    """Moving average prediction model"""

    def __init__(self, window_size: int = 5):
        super().__init__(PredictionModel.TIME_SERIES)
        self.window_size = window_size

    async def train(self, data: List[MetricData]) -> bool:
        """Train moving average model"""
        if not self._validate_data(data, self.window_size):
            return False

        self.is_trained = True
        self.last_trained = datetime.utcnow()

        # Calculate accuracy using cross-validation
        values = [d.value for d in data]
        predictions = []
        actuals = []

        for i in range(self.window_size, len(values)):
            window = values[i-self.window_size:i]
            pred = sum(window) / len(window)
            predictions.append(pred)
            actuals.append(values[i])

        self.accuracy_score = self._calculate_confidence(predictions, actuals)
        return True

    async def predict(self, data: List[MetricData], horizon: int = 3600) -> Optional[Dict[str, Any]]:
        """Make moving average prediction"""
        if not self.is_trained or not data:
            return None

        values = [d.value for d in data[-self.window_size:]]
        if len(values) < self.window_size:
            return None

        prediction = sum(values) / len(values)

        return {
            "value": max(0, prediction),
            "confidence": self.accuracy_score,
            "method": "moving_average",
            "window_size": self.window_size
        }

class ExponentialSmoothing(BaseMLModel):
    """Exponential smoothing for time series prediction"""

    def __init__(self, alpha: float = 0.3):
        super().__init__(PredictionModel.TIME_SERIES)
        self.alpha = alpha
        self.smoothed_value: Optional[float] = None

    async def train(self, data: List[MetricData]) -> bool:
        """Train exponential smoothing model"""
        if not self._validate_data(data, 3):
            return False

        values = [d.value for d in data]

        # Initialize with first value
        self.smoothed_value = values[0]

        # Apply exponential smoothing
        for value in values[1:]:
            self.smoothed_value = self.alpha * value + (1 - self.alpha) * self.smoothed_value

        self.is_trained = True
        self.last_trained = datetime.utcnow()

        # Calculate accuracy
        predictions = [values[0]]  # First prediction is initial value
        smoothed = values[0]

        for i in range(1, len(values)):
            smoothed = self.alpha * values[i-1] + (1 - self.alpha) * smoothed
            predictions.append(smoothed)

        self.accuracy_score = self._calculate_confidence(predictions, values)
        return True

    async def predict(self, data: List[MetricData], horizon: int = 3600) -> Optional[Dict[str, Any]]:
        """Make exponential smoothing prediction"""
        if not self.is_trained or self.smoothed_value is None or not data:
            return None

        # Use latest smoothed value as prediction
        latest_value = data[-1].value
        prediction = self.alpha * latest_value + (1 - self.alpha) * self.smoothed_value

        # Update smoothed value
        self.smoothed_value = prediction

        return {
            "value": max(0, prediction),
            "confidence": self.accuracy_score,
            "method": "exponential_smoothing",
            "alpha": self.alpha
        }

class SimpleAnomalyDetector(BaseMLModel):
    """Simple statistical anomaly detection"""

    def __init__(self, threshold: float = 3.0):
        super().__init__(PredictionModel.ANOMALY_DETECTION)
        self.threshold = threshold
        self.mean: Optional[float] = None
        self.std_dev: Optional[float] = None

    async def train(self, data: List[MetricData]) -> bool:
        """Train anomaly detection model"""
        if not self._validate_data(data, 5):
            return False

        values = [d.value for d in data]

        self.mean = statistics.mean(values)
        self.std_dev = statistics.stdev(values) if len(values) > 1 else 0

        self.is_trained = True
        self.last_trained = datetime.utcnow()
        self.accuracy_score = 0.8  # Default confidence for anomaly detection

        return True

    async def predict(self, data: List[MetricData], horizon: int = 3600) -> Optional[Dict[str, Any]]:
        """Detect anomalies in latest data"""
        if not self.is_trained or self.mean is None or self.std_dev is None or not data:
            return None

        latest_value = data[-1].value

        # Calculate z-score
        if self.std_dev == 0:
            z_score = 0
        else:
            z_score = abs(latest_value - self.mean) / self.std_dev

        is_anomaly = z_score > self.threshold

        return {
            "value": latest_value,
            "is_anomaly": is_anomaly,
            "z_score": z_score,
            "threshold": self.threshold,
            "confidence": self.accuracy_score,
            "method": "statistical_anomaly_detection"
        }

class TrendAnalyzer(BaseMLModel):
    """Advanced trend analysis with multiple indicators"""

    def __init__(self):
        super().__init__(PredictionModel.CLASSIFICATION)
        self.trend_indicators: Dict[str, Any] = {}

    async def train(self, data: List[MetricData]) -> bool:
        """Train trend analysis model"""
        if not self._validate_data(data, 10):
            return False

        values = [d.value for d in data]

        # Calculate trend indicators
        self.trend_indicators = {
            "linear_trend": self._calculate_linear_trend(values),
            "moving_average": self._calculate_moving_average(values, 5),
            "volatility": self._calculate_volatility(values),
            "momentum": self._calculate_momentum(values)
        }

        self.is_trained = True
        self.last_trained = datetime.utcnow()
        self.accuracy_score = 0.75  # Default confidence for trend analysis

        return True

    async def predict(self, data: List[MetricData], horizon: int = 3600) -> Optional[Dict[str, Any]]:
        """Analyze trend and predict direction"""
        if not self.is_trained or not data:
            return None

        values = [d.value for d in data[-10:]]  # Last 10 data points

        # Analyze current trend
        current_trend = self._analyze_current_trend(values)

        # Predict next value based on trend
        prediction = self._predict_from_trend(values, current_trend)

        return {
            "value": max(0, prediction),
            "trend": current_trend["direction"],
            "strength": current_trend["strength"],
            "confidence": self.accuracy_score,
            "indicators": self.trend_indicators,
            "method": "trend_analysis"
        }

    def _calculate_linear_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate linear trend"""
        n = len(values)
        x = list(range(n))
        slope = np.polyfit(x, values, 1)[0]

        return {
            "slope": slope,
            "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        }

    def _calculate_moving_average(self, values: List[float], window: int) -> float:
        """Calculate moving average"""
        if len(values) < window:
            return sum(values) / len(values)
        return sum(values[-window:]) / window

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (coefficient of variation)"""
        if len(values) <= 1:
            return 0

        mean = statistics.mean(values)
        if mean == 0:
            return 0

        std_dev = statistics.stdev(values)
        return std_dev / mean

    def _calculate_momentum(self, values: List[float]) -> float:
        """Calculate momentum indicator"""
        if len(values) < 2:
            return 0

        return (values[-1] - values[0]) / max(abs(values[0]), 0.01)

    def _analyze_current_trend(self, values: List[float]) -> Dict[str, Any]:
        """Analyze current trend direction and strength"""
        if len(values) < 3:
            return {"direction": "unknown", "strength": 0}

        # Simple trend analysis
        recent = values[-3:]
        trend = (recent[-1] - recent[0]) / max(abs(recent[0]), 0.01)

        if abs(trend) < 0.05:
            direction = "stable"
            strength = 0
        elif trend > 0:
            direction = "increasing"
            strength = min(abs(trend), 1.0)
        else:
            direction = "decreasing"
            strength = min(abs(trend), 1.0)

        return {
            "direction": direction,
            "strength": strength,
            "change_percent": trend
        }

    def _predict_from_trend(self, values: List[float], trend: Dict[str, Any]) -> float:
        """Predict next value based on trend analysis"""
        if trend["direction"] == "stable":
            return values[-1]
        elif trend["direction"] == "increasing":
            return values[-1] * (1 + trend["strength"] * 0.1)
        else:
            return values[-1] * (1 - trend["strength"] * 0.1)

# Global ML model registry
ml_registry = MLModelRegistry()

async def get_ml_model(model_type: PredictionModel) -> Optional[BaseMLModel]:
    """Get ML model instance"""
    return ml_registry.get_model(model_type)

async def predict_with_model(model_type: PredictionModel, data: List[MetricData],
                           horizon: int = 3600) -> Optional[Dict[str, Any]]:
    """Make prediction using specified model"""
    model = await get_ml_model(model_type)
    if not model:
        return None

    # Train model if not trained or training is old
    if not model.is_trained or \
       (model.last_trained and (datetime.utcnow() - model.last_trained).seconds > 3600):
        await model.train(data)

    # Make prediction
    return await model.predict(data, horizon)

# Utility functions for advanced analytics

async def detect_seasonality(data: List[MetricData], period: int = 24) -> Dict[str, Any]:
    """Detect seasonality in time series data"""
    if len(data) < period * 2:
        return {"seasonal": False, "period": None, "strength": 0}

    values = [d.value for d in data]

    # Simple autocorrelation analysis
    correlations = []
    for lag in range(1, min(period + 1, len(values) // 2)):
        corr = np.corrcoef(values[:-lag], values[lag:])[0, 1]
        correlations.append(abs(corr))

    max_corr = max(correlations) if correlations else 0
    best_period = correlations.index(max_corr) + 1 if correlations else 0

    return {
        "seasonal": max_corr > 0.6,
        "period": best_period if max_corr > 0.6 else None,
        "strength": max_corr,
        "method": "autocorrelation"
    }

async def cluster_users_by_behavior(data: List[Dict[str, Any]], n_clusters: int = 3) -> Dict[str, List[str]]:
    """Cluster users by behavior patterns"""
    if len(data) < n_clusters:
        return {}

    # Simple k-means like clustering
    users = [d["user_id"] for d in data]
    features = [[d.get("page_views", 0), d.get("session_duration", 0),
                d.get("actions_count", 0)] for d in data]

    # Normalize features
    features_array = np.array(features)
    if features_array.shape[0] == 0:
        return {}

    # Simple clustering by quantiles
    clusters = defaultdict(list)

    for i, user in enumerate(users):
        # Simple clustering based on activity level
        activity_score = sum(features[i]) if i < len(features) else 0

        if activity_score > 100:
            cluster = "high_activity"
        elif activity_score > 50:
            cluster = "medium_activity"
        else:
            cluster = "low_activity"

        clusters[cluster].append(user)

    return dict(clusters)

async def calculate_user_lifetime_value(predictions: List[Dict[str, Any]],
                                      current_value: float) -> Dict[str, Any]:
    """Calculate predicted user lifetime value"""
    if not predictions:
        return {"current_value": current_value, "predicted_value": current_value}

    # Simple LTV calculation
    predicted_revenue = sum(p.get("value", 0) for p in predictions)
    total_value = current_value + predicted_revenue

    return {
        "current_value": current_value,
        "predicted_value": total_value,
        "predicted_revenue": predicted_revenue,
        "confidence": statistics.mean([p.get("confidence", 0) for p in predictions])
    }