"""
A/B Testing Framework for Proyecto Semilla
Advanced experimentation platform with statistical significance testing
"""

import json
import random
import statistics
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import uuid

from .models import ABTestModel, MetricData
from .engine import RealTimeAnalyticsEngine

class TestStatus(Enum):
    """A/B test status"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"

class VariantType(Enum):
    """Variant types"""
    CONTROL = "control"
    TREATMENT = "treatment"

@dataclass
class ABTestVariant:
    """A/B test variant configuration"""
    id: str
    name: str
    type: VariantType
    config: Dict[str, Any]
    traffic_percentage: float
    user_count: int = 0
    conversion_count: int = 0

@dataclass
class ABTestResult:
    """A/B test results"""
    test_id: str
    variant_results: Dict[str, Dict[str, Any]]
    winner: Optional[str]
    confidence_level: float
    statistical_significance: bool
    improvement_percentage: float
    sample_size: int
    test_duration_days: int

class StatisticalCalculator:
    """Statistical calculations for A/B testing"""

    @staticmethod
    def calculate_conversion_rate(conversions: int, visitors: int) -> float:
        """Calculate conversion rate"""
        return conversions / visitors if visitors > 0 else 0

    @staticmethod
    def calculate_confidence_interval(conversion_rate: float, visitors: int,
                                   confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval using Wilson score interval"""
        if visitors == 0:
            return (0, 0)

        z_score = 1.96  # 95% confidence
        if confidence_level == 0.99:
            z_score = 2.576

        # Wilson score interval
        n = visitors
        p = conversion_rate

        denominator = 1 + z_score**2 / n
        center = (p + z_score**2 / (2 * n)) / denominator
        interval = z_score * math.sqrt(p * (1 - p) / n + z_score**2 / (4 * n**2)) / denominator

        return (center - interval, center + interval)

    @staticmethod
    def calculate_statistical_significance(variant_a: Dict[str, Any],
                                        variant_b: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical significance between two variants"""
        conv_a = variant_a["conversions"]
        visitors_a = variant_a["visitors"]
        conv_b = variant_b["conversions"]
        visitors_b = variant_b["visitors"]

        if visitors_a == 0 or visitors_b == 0:
            return {
                "significant": False,
                "p_value": 1.0,
                "z_score": 0,
                "confidence_level": 0
            }

        # Calculate conversion rates
        rate_a = conv_a / visitors_a
        rate_b = conv_b / visitors_b

        # Pooled standard error
        se_a = math.sqrt(rate_a * (1 - rate_a) / visitors_a)
        se_b = math.sqrt(rate_b * (1 - rate_b) / visitors_b)
        se_diff = math.sqrt(se_a**2 + se_b**2)

        if se_diff == 0:
            return {
                "significant": False,
                "p_value": 1.0,
                "z_score": 0,
                "confidence_level": 0
            }

        # Z-score
        z_score = abs(rate_a - rate_b) / se_diff

        # P-value (approximation)
        p_value = 2 * (1 - StatisticsCalculator._normal_cdf(z_score))

        # Confidence level
        confidence_level = (1 - p_value) * 100

        return {
            "significant": p_value < 0.05,  # 95% confidence
            "p_value": p_value,
            "z_score": z_score,
            "confidence_level": confidence_level
        }

    @staticmethod
    def _normal_cdf(x: float) -> float:
        """Approximate normal cumulative distribution function"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    @staticmethod
    def calculate_minimum_sample_size(baseline_rate: float, minimum_detectable_effect: float,
                                    power: float = 0.8, alpha: float = 0.05) -> int:
        """Calculate minimum sample size needed for statistical significance"""
        # Simplified calculation
        z_alpha = 1.96  # 95% confidence
        z_beta = 0.84   # 80% power

        p1 = baseline_rate
        p2 = baseline_rate * (1 + minimum_detectable_effect)

        numerator = (z_alpha * math.sqrt(2 * p1 * (1 - p1)) +
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        denominator = (p1 - p2)**2

        if denominator == 0:
            return 1000  # Default minimum

        return int(math.ceil(numerator / denominator))

class ABTestingEngine:
    """
    Advanced A/B testing engine with real-time analytics
    """

    def __init__(self, analytics_engine: RealTimeAnalyticsEngine, redis_client=None):
        self.analytics_engine = analytics_engine
        self.redis = redis_client
        self.active_tests: Dict[str, Dict[str, Any]] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {test_id: variant_id}

    async def create_test(self, config: Dict[str, Any]) -> str:
        """Create a new A/B test"""
        test_id = str(uuid.uuid4())

        # Validate configuration
        self._validate_test_config(config)

        # Create variants
        variants = []
        for variant_config in config["variants"]:
            variant = ABTestVariant(
                id=str(uuid.uuid4()),
                name=variant_config["name"],
                type=VariantType.TREATMENT if variant_config.get("type") == "treatment" else VariantType.CONTROL,
                config=variant_config.get("config", {}),
                traffic_percentage=variant_config["traffic_percentage"]
            )
            variants.append(variant)

        # Ensure traffic percentages sum to 100%
        total_traffic = sum(v["traffic_percentage"] for v in config["variants"])
        if abs(total_traffic - 100) > 0.1:
            raise ValueError("Traffic percentages must sum to 100%")

        test_data = {
            "id": test_id,
            "name": config["name"],
            "description": config.get("description", ""),
            "target_metric": config["target_metric"],
            "variants": [asdict(v) for v in variants],
            "start_date": datetime.utcnow(),
            "end_date": None,
            "status": TestStatus.DRAFT.value,
            "winner": None,
            "minimum_sample_size": config.get("minimum_sample_size", 1000),
            "confidence_threshold": config.get("confidence_threshold", 95)
        }

        self.active_tests[test_id] = test_data

        # Cache in Redis if available
        if self.redis:
            await self.redis.setex(
                f"ab_test:{test_id}",
                86400 * 30,  # 30 days
                json.dumps(test_data)
            )

        return test_id

    async def start_test(self, test_id: str) -> bool:
        """Start an A/B test"""
        if test_id not in self.active_tests:
            return False

        test = self.active_tests[test_id]
        test["status"] = TestStatus.RUNNING.value
        test["start_date"] = datetime.utcnow()

        # Update Redis
        if self.redis:
            await self.redis.setex(
                f"ab_test:{test_id}",
                86400 * 30,
                json.dumps(test)
            )

        return True

    async def stop_test(self, test_id: str) -> bool:
        """Stop an A/B test"""
        if test_id not in self.active_tests:
            return False

        test = self.active_tests[test_id]
        test["status"] = TestStatus.STOPPED.value
        test["end_date"] = datetime.utcnow()

        # Update Redis
        if self.redis:
            await self.redis.setex(
                f"ab_test:{test_id}",
                86400 * 30,
                json.dumps(test)
            )

        return True

    async def assign_user_to_variant(self, user_id: str, test_id: str) -> Optional[str]:
        """Assign user to a test variant"""
        if test_id not in self.active_tests:
            return None

        test = self.active_tests[test_id]
        if test["status"] != TestStatus.RUNNING.value:
            return None

        # Check if user is already assigned
        if user_id not in self.user_assignments:
            self.user_assignments[user_id] = {}

        if test_id in self.user_assignments[user_id]:
            return self.user_assignments[user_id][test_id]

        # Assign user to variant based on traffic percentages
        variant = self._assign_variant(test["variants"])
        self.user_assignments[user_id][test_id] = variant["id"]

        # Update variant user count
        for v in test["variants"]:
            if v["id"] == variant["id"]:
                v["user_count"] += 1
                break

        return variant["id"]

    async def track_conversion(self, user_id: str, test_id: str, metric_value: float = 1.0):
        """Track conversion for a user in a test"""
        if test_id not in self.active_tests:
            return

        test = self.active_tests[test_id]
        if test["status"] != TestStatus.RUNNING.value:
            return

        # Find user's variant
        user_assignments = self.user_assignments.get(user_id, {})
        variant_id = user_assignments.get(test_id)

        if not variant_id:
            return

        # Update conversion count
        for variant in test["variants"]:
            if variant["id"] == variant_id:
                variant["conversion_count"] += metric_value
                break

        # Check if test should be completed
        await self._check_test_completion(test_id)

    async def get_test_results(self, test_id: str) -> Optional[ABTestResult]:
        """Get comprehensive test results"""
        if test_id not in self.active_tests:
            return None

        test = self.active_tests[test_id]

        # Calculate results for each variant
        variant_results = {}
        control_variant = None

        for variant in test["variants"]:
            conversion_rate = StatisticalCalculator.calculate_conversion_rate(
                variant["conversion_count"], variant["user_count"]
            )

            confidence_interval = StatisticalCalculator.calculate_confidence_interval(
                conversion_rate, variant["user_count"]
            )

            variant_results[variant["name"]] = {
                "variant_id": variant["id"],
                "visitors": variant["user_count"],
                "conversions": variant["conversion_count"],
                "conversion_rate": conversion_rate,
                "confidence_interval": confidence_interval
            }

            if variant["type"] == VariantType.CONTROL.value:
                control_variant = variant["name"]

        # Calculate statistical significance
        winner = None
        statistical_significance = False
        improvement_percentage = 0

        if control_variant and len(variant_results) > 1:
            control_results = variant_results[control_variant]

            for variant_name, results in variant_results.items():
                if variant_name == control_variant:
                    continue

                significance = StatisticalCalculator.calculate_statistical_significance(
                    control_results, results
                )

                if significance["significant"]:
                    statistical_significance = True
                    improvement = ((results["conversion_rate"] - control_results["conversion_rate"]) /
                                 control_results["conversion_rate"]) * 100

                    if improvement > improvement_percentage:
                        improvement_percentage = improvement
                        winner = variant_name

        # Calculate test duration
        start_date = test["start_date"]
        end_date = test.get("end_date") or datetime.utcnow()
        test_duration_days = (end_date - start_date).days

        # Calculate total sample size
        sample_size = sum(v["user_count"] for v in test["variants"])

        return ABTestResult(
            test_id=test_id,
            variant_results=variant_results,
            winner=winner,
            confidence_level=test.get("confidence_threshold", 95),
            statistical_significance=statistical_significance,
            improvement_percentage=improvement_percentage,
            sample_size=sample_size,
            test_duration_days=test_duration_days
        )

    async def get_recommendations(self, test_id: str) -> List[Dict[str, Any]]:
        """Get recommendations for test optimization"""
        recommendations = []

        test = self.active_tests.get(test_id)
        if not test:
            return recommendations

        results = await self.get_test_results(test_id)
        if not results:
            return recommendations

        # Check sample size
        min_sample = test.get("minimum_sample_size", 1000)
        if results.sample_size < min_sample:
            recommendations.append({
                "type": "sample_size",
                "priority": "high",
                "message": f"Test needs {min_sample - results.sample_size} more visitors for statistical significance",
                "action": "Continue running test"
            })

        # Check test duration
        if results.test_duration_days < 7:
            recommendations.append({
                "type": "duration",
                "priority": "medium",
                "message": "Test should run for at least 7 days to account for weekly patterns",
                "action": "Continue running test"
            })

        # Check for early stopping
        if results.statistical_significance and results.improvement_percentage > 10:
            recommendations.append({
                "type": "early_stopping",
                "priority": "high",
                "message": f"Winner detected with {results.improvement_percentage:.1f}% improvement",
                "action": "Stop test and implement winner"
            })

        return recommendations

    def _validate_test_config(self, config: Dict[str, Any]):
        """Validate A/B test configuration"""
        required_fields = ["name", "target_metric", "variants"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        if len(config["variants"]) < 2:
            raise ValueError("Test must have at least 2 variants")

        # Validate traffic percentages
        total_traffic = sum(v.get("traffic_percentage", 0) for v in config["variants"])
        if abs(total_traffic - 100) > 0.1:
            raise ValueError("Traffic percentages must sum to 100%")

    def _assign_variant(self, variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assign user to variant based on traffic percentages"""
        rand = random.random() * 100
        cumulative = 0

        for variant in variants:
            cumulative += variant["traffic_percentage"]
            if rand <= cumulative:
                return variant

        # Fallback to first variant
        return variants[0]

    async def _check_test_completion(self, test_id: str):
        """Check if test should be completed"""
        test = self.active_tests.get(test_id)
        if not test:
            return

        results = await self.get_test_results(test_id)
        if not results:
            return

        # Auto-complete conditions
        min_sample = test.get("minimum_sample_size", 1000)
        confidence_threshold = test.get("confidence_threshold", 95)

        if (results.sample_size >= min_sample and
            results.confidence_level >= confidence_threshold and
            results.statistical_significance):

            test["status"] = TestStatus.COMPLETED.value
            test["end_date"] = datetime.utcnow()
            test["winner"] = results.winner

            # Update Redis
            if self.redis:
                await self.redis.setex(
                    f"ab_test:{test_id}",
                    86400 * 30,
                    json.dumps(test)
                )

class ABTestTemplates:
    """Predefined A/B test templates"""

    @staticmethod
    def landing_page_test() -> Dict[str, Any]:
        """Landing page optimization test"""
        return {
            "name": "Landing Page Optimization",
            "description": "Test different landing page designs",
            "target_metric": "conversion_rate",
            "variants": [
                {
                    "name": "control",
                    "type": "control",
                    "traffic_percentage": 50,
                    "config": {"design": "original"}
                },
                {
                    "name": "new_design",
                    "type": "treatment",
                    "traffic_percentage": 50,
                    "config": {"design": "modern"}
                }
            ],
            "minimum_sample_size": 2000,
            "confidence_threshold": 95
        }

    @staticmethod
    def pricing_test() -> Dict[str, Any]:
        """Pricing strategy test"""
        return {
            "name": "Pricing Strategy Test",
            "description": "Test different pricing models",
            "target_metric": "revenue_per_user",
            "variants": [
                {
                    "name": "current_pricing",
                    "type": "control",
                    "traffic_percentage": 50,
                    "config": {"pricing": "monthly"}
                },
                {
                    "name": "annual_discount",
                    "type": "treatment",
                    "traffic_percentage": 50,
                    "config": {"pricing": "annual"}
                }
            ],
            "minimum_sample_size": 1000,
            "confidence_threshold": 95
        }

    @staticmethod
    def feature_adoption_test() -> Dict[str, Any]:
        """Feature adoption test"""
        return {
            "name": "Feature Adoption Test",
            "description": "Test feature rollout strategies",
            "target_metric": "feature_usage_rate",
            "variants": [
                {
                    "name": "no_onboarding",
                    "type": "control",
                    "traffic_percentage": 50,
                    "config": {"onboarding": False}
                },
                {
                    "name": "guided_onboarding",
                    "type": "treatment",
                    "traffic_percentage": 50,
                    "config": {"onboarding": True}
                }
            ],
            "minimum_sample_size": 1500,
            "confidence_threshold": 95
        }

# Global A/B testing engine instance
ab_testing_engine = ABTestingEngine(None)  # Will be initialized with analytics engine

async def get_ab_testing_engine() -> ABTestingEngine:
    """Dependency injection for A/B testing engine"""
    return ab_testing_engine

async def initialize_ab_testing_engine(analytics_engine: RealTimeAnalyticsEngine):
    """Initialize A/B testing engine with analytics engine"""
    global ab_testing_engine
    ab_testing_engine = ABTestingEngine(analytics_engine)