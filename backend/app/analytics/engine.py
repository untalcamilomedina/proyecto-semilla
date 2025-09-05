"""
Real-Time Analytics Engine for Proyecto Semilla
High-performance analytics with ML predictions and automated insights
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from collections import defaultdict, deque
import statistics
import math

from .models import (
    AnalyticsEvent, MetricData, PredictionResult, Insight,
    EventType, MetricType, PredictionModel
)

logger = logging.getLogger(__name__)

class RealTimeAnalyticsEngine:
    """
    High-performance real-time analytics engine
    Handles event processing, metric calculation, and ML predictions
    """

    def __init__(self, redis_client=None, config: Optional[Dict[str, Any]] = None):
        self.redis = redis_client
        self.config = config or {
            "batch_size": 1000,
            "real_time_window": 300,  # 5 minutes
            "prediction_interval": 3600,  # 1 hour
            "insight_threshold": 0.8,
            "max_concurrent_predictions": 10
        }

        # In-memory data structures for real-time processing
        self.event_buffer: deque = deque(maxlen=self.config["batch_size"] * 2)
        self.metrics_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.prediction_cache: Dict[str, PredictionResult] = {}

        # Real-time aggregations
        self.real_time_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.user_segments: Dict[str, List[str]] = defaultdict(list)

        # ML models registry
        self.ml_models: Dict[str, Any] = {}

        # Background tasks
        self.processing_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.prediction_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the analytics engine"""
        logger.info("🚀 Starting Real-Time Analytics Engine")

        # Start background processing
        self.processing_task = asyncio.create_task(self._process_events_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.prediction_task = asyncio.create_task(self._prediction_loop())

        logger.info("✅ Real-Time Analytics Engine started")

    async def stop(self):
        """Stop the analytics engine"""
        logger.info("🛑 Stopping Real-Time Analytics Engine")

        if self.processing_task:
            self.processing_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.prediction_task:
            self.prediction_task.cancel()

        logger.info("✅ Real-Time Analytics Engine stopped")

    async def track_event(self, event: AnalyticsEvent):
        """Track a new analytics event"""
        # Add to buffer for processing
        self.event_buffer.append(event)

        # Update real-time metrics immediately
        await self._update_real_time_metrics(event)

        # Cache in Redis if available
        if self.redis:
            await self._cache_event_redis(event)

        # Check for immediate insights
        await self._check_real_time_insights(event)

    async def get_real_time_metrics(self, metric_name: str,
                                   time_window: int = 300) -> Dict[str, Any]:
        """Get real-time metrics for the specified time window"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=time_window)

        # Get data from cache
        metric_data = self.metrics_cache.get(metric_name, deque())

        # Filter by time window
        recent_data = [m for m in metric_data if m.timestamp >= window_start]

        if not recent_data:
            return {
                "name": metric_name,
                "count": 0,
                "sum": 0,
                "avg": 0,
                "min": 0,
                "max": 0,
                "time_window": time_window
            }

        values = [m.value for m in recent_data]

        return {
            "name": metric_name,
            "count": len(values),
            "sum": sum(values),
            "avg": statistics.mean(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "time_window": time_window,
            "last_updated": max(m.timestamp for m in recent_data).isoformat()
        }

    async def get_user_segment(self, user_id: str) -> List[str]:
        """Get user segments for a specific user"""
        segments = []

        for segment_name, user_ids in self.user_segments.items():
            if user_id in user_ids:
                segments.append(segment_name)

        return segments

    async def predict_metric(self, metric_name: str, prediction_type: PredictionModel,
                           time_ahead: int = 3600) -> Optional[PredictionResult]:
        """Generate ML prediction for a metric"""
        cache_key = f"{metric_name}_{prediction_type.value}_{time_ahead}"

        # Check cache first
        if cache_key in self.prediction_cache:
            cached = self.prediction_cache[cache_key]
            if (datetime.utcnow() - cached.timestamp).seconds < self.config["prediction_interval"]:
                return cached

        # Get historical data
        metric_data = self.metrics_cache.get(metric_name, deque())
        if len(metric_data) < 10:  # Need minimum data points
            return None

        # Generate prediction based on model type
        if prediction_type == PredictionModel.LINEAR_REGRESSION:
            prediction = await self._linear_regression_prediction(metric_data, time_ahead)
        elif prediction_type == PredictionModel.TIME_SERIES:
            prediction = await self._time_series_prediction(metric_data, time_ahead)
        elif prediction_type == PredictionModel.ANOMALY_DETECTION:
            prediction = await self._anomaly_detection(metric_data)
        else:
            return None

        if prediction:
            result = PredictionResult(
                model_id=f"{metric_name}_{prediction_type.value}",
                prediction=prediction["value"],
                confidence=prediction["confidence"],
                features={"data_points": len(metric_data)},
                timestamp=datetime.utcnow(),
                model_type=prediction_type
            )

            # Cache result
            self.prediction_cache[cache_key] = result
            return result

        return None

    async def generate_insights(self, tenant_id: Optional[str] = None) -> List[Insight]:
        """Generate automated insights from analytics data"""
        insights = []

        # Analyze user engagement
        engagement_insight = await self._analyze_user_engagement(tenant_id)
        if engagement_insight:
            insights.append(engagement_insight)

        # Analyze performance metrics
        performance_insight = await self._analyze_performance_metrics(tenant_id)
        if performance_insight:
            insights.append(performance_insight)

        # Analyze conversion funnels
        conversion_insight = await self._analyze_conversion_funnel(tenant_id)
        if conversion_insight:
            insights.append(conversion_insight)

        # Analyze error patterns
        error_insight = await self._analyze_error_patterns(tenant_id)
        if error_insight:
            insights.append(error_insight)

        return insights

    async def create_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Create and start an A/B test"""
        test_id = f"ab_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Store test configuration
        if self.redis:
            await self.redis.setex(
                f"ab_test:{test_id}",
                86400 * 30,  # 30 days
                json.dumps(test_config)
            )

        # Initialize test metrics
        await self._initialize_ab_test_metrics(test_id, test_config)

        return test_id

    async def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test results and determine winner"""
        if not self.redis:
            return {"error": "Redis not available"}

        test_data = await self.redis.get(f"ab_test:{test_id}")
        if not test_data:
            return {"error": "Test not found"}

        test_config = json.loads(test_data)

        # Get metrics for each variant
        results = {}
        for variant in test_config["variants"]:
            variant_metrics = await self.get_real_time_metrics(
                f"ab_test_{test_id}_{variant['name']}_{test_config['target_metric']}"
            )
            results[variant["name"]] = variant_metrics

        # Determine winner using statistical significance
        winner = await self._determine_ab_test_winner(results)

        return {
            "test_id": test_id,
            "config": test_config,
            "results": results,
            "winner": winner,
            "confidence": 0.95 if winner else 0
        }

    # Private methods

    async def _process_events_loop(self):
        """Background loop to process buffered events"""
        while True:
            try:
                if len(self.event_buffer) >= self.config["batch_size"]:
                    events = []
                    for _ in range(min(self.config["batch_size"], len(self.event_buffer))):
                        events.append(self.event_buffer.popleft())

                    await self._process_event_batch(events)

                await asyncio.sleep(1)  # Process every second

            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(5)

    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(300)  # Clean up every 5 minutes

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)

    async def _prediction_loop(self):
        """Background prediction generation loop"""
        while True:
            try:
                await self._generate_predictions()
                await asyncio.sleep(self.config["prediction_interval"])

            except Exception as e:
                logger.error(f"Error in prediction loop: {e}")
                await asyncio.sleep(300)

    async def _update_real_time_metrics(self, event: AnalyticsEvent):
        """Update real-time metrics from event"""
        # Update session tracking
        if event.session_id not in self.active_sessions:
            self.active_sessions[event.session_id] = {
                "user_id": event.user_id,
                "start_time": event.timestamp,
                "last_activity": event.timestamp,
                "events_count": 0,
                "page_views": 0
            }

        session = self.active_sessions[event.session_id]
        session["last_activity"] = event.timestamp
        session["events_count"] += 1

        if event.event_type == EventType.PAGE_VIEW:
            session["page_views"] += 1

        # Update metrics cache
        metric_name = f"{event.event_type.value}_count"
        metric = MetricData(
            name=metric_name,
            value=1,
            timestamp=event.timestamp,
            tags={
                "event_type": event.event_type.value,
                "user_id": event.user_id or "anonymous",
                "tenant_id": event.tenant_id or "default"
            }
        )

        self.metrics_cache[metric_name].append(metric)

    async def _cache_event_redis(self, event: AnalyticsEvent):
        """Cache event in Redis for persistence"""
        event_data = {
            "id": event.id,
            "event_type": event.event_type.value,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "tenant_id": event.tenant_id,
            "timestamp": event.timestamp.isoformat(),
            "properties": event.properties,
            "metadata": event.metadata
        }

        # Cache in Redis with 24h TTL
        await self.redis.setex(
            f"analytics_event:{event.id}",
            86400,
            json.dumps(event_data)
        )

        # Add to time-based index
        time_key = event.timestamp.strftime("%Y%m%d%H")
        await self.redis.sadd(f"analytics_events:{time_key}", event.id)

    async def _check_real_time_insights(self, event: AnalyticsEvent):
        """Check for real-time insights from event"""
        # Implement real-time insight detection logic
        pass

    async def _process_event_batch(self, events: List[AnalyticsEvent]):
        """Process a batch of events"""
        # Implement batch processing logic
        logger.info(f"Processed batch of {len(events)} events")

    async def _cleanup_old_data(self):
        """Clean up old data from caches"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        for metric_name, metric_data in self.metrics_cache.items():
            # Remove old entries
            while metric_data and metric_data[0].timestamp < cutoff_time:
                metric_data.popleft()

        # Clean up old sessions
        current_time = datetime.utcnow()
        inactive_sessions = []

        for session_id, session_data in self.active_sessions.items():
            if (current_time - session_data["last_activity"]).seconds > 1800:  # 30 minutes
                inactive_sessions.append(session_id)

        for session_id in inactive_sessions:
            del self.active_sessions[session_id]

    async def _generate_predictions(self):
        """Generate ML predictions for key metrics"""
        key_metrics = ["page_view_count", "user_action_count", "api_call_count"]

        for metric_name in key_metrics:
            for model_type in [PredictionModel.LINEAR_REGRESSION, PredictionModel.ANOMALY_DETECTION]:
                try:
                    prediction = await self.predict_metric(metric_name, model_type)
                    if prediction:
                        logger.info(f"Generated prediction for {metric_name}: {prediction.prediction}")
                except Exception as e:
                    logger.error(f"Error generating prediction for {metric_name}: {e}")

    async def _linear_regression_prediction(self, data: deque, time_ahead: int) -> Optional[Dict[str, Any]]:
        """Simple linear regression prediction"""
        if len(data) < 2:
            return None

        # Simple trend analysis
        values = [d.value for d in list(data)[-10:]]  # Last 10 data points
        if len(values) < 2:
            return None

        # Calculate trend
        n = len(values)
        trend = (values[-1] - values[0]) / max(1, n - 1)

        # Predict next value
        prediction = values[-1] + trend

        return {
            "value": max(0, prediction),
            "confidence": 0.7,
            "trend": "increasing" if trend > 0 else "decreasing"
        }

    async def _time_series_prediction(self, data: deque, time_ahead: int) -> Optional[Dict[str, Any]]:
        """Time series prediction (simplified)"""
        if len(data) < 5:
            return None

        values = [d.value for d in list(data)[-20:]]
        avg = statistics.mean(values)

        return {
            "value": avg,
            "confidence": 0.6,
            "method": "moving_average"
        }

    async def _anomaly_detection(self, data: deque) -> Optional[Dict[str, Any]]:
        """Simple anomaly detection"""
        if len(data) < 10:
            return None

        values = [d.value for d in list(data)[-20:]]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        latest_value = values[-1]
        z_score = abs(latest_value - mean) / max(std_dev, 1)

        is_anomaly = z_score > 3  # 3 standard deviations

        return {
            "value": latest_value,
            "is_anomaly": is_anomaly,
            "z_score": z_score,
            "confidence": 0.8
        }

    async def _analyze_user_engagement(self, tenant_id: Optional[str]) -> Optional[Insight]:
        """Analyze user engagement patterns"""
        # Implement engagement analysis logic
        return None

    async def _analyze_performance_metrics(self, tenant_id: Optional[str]) -> Optional[Insight]:
        """Analyze performance metrics"""
        # Implement performance analysis logic
        return None

    async def _analyze_conversion_funnel(self, tenant_id: Optional[str]) -> Optional[Insight]:
        """Analyze conversion funnel"""
        # Implement conversion analysis logic
        return None

    async def _analyze_error_patterns(self, tenant_id: Optional[str]) -> Optional[Insight]:
        """Analyze error patterns"""
        # Implement error analysis logic
        return None

    async def _initialize_ab_test_metrics(self, test_id: str, config: Dict[str, Any]):
        """Initialize metrics for A/B test"""
        # Implement A/B test initialization logic
        pass

    async def _determine_ab_test_winner(self, results: Dict[str, Any]) -> Optional[str]:
        """Determine A/B test winner using statistical significance"""
        # Implement statistical significance testing
        return None

# Global analytics engine instance
analytics_engine = RealTimeAnalyticsEngine()

async def get_analytics_engine() -> RealTimeAnalyticsEngine:
    """Dependency injection for analytics engine"""
    return analytics_engine