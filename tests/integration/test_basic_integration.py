"""
Basic integration tests for Proyecto Semilla
"""

import pytest


class TestBasicIntegration:
    """Basic integration test cases"""

    def test_imports_work(self):
        """Test that all main modules can be imported"""
        try:
            from app.core.config import settings
            from app.core.database import get_db
            from app.core.security import get_current_user
            from app.core.metrics import VibecodingMetrics
            from app.core.alerting import AlertingEngine
            from app.core.circuit_breaker import CircuitBreaker
            from app.core.auto_recovery import AutoRecoveryEngine
            from app.core.error_handler import ErrorHandler

            # If we get here, all imports worked
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")

    def test_core_components_initialization(self):
        """Test that core components can be initialized"""
        try:
            from app.core.metrics import VibecodingMetrics
            from app.core.alerting import AlertingEngine
            from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
            from app.core.auto_recovery import AutoRecoveryEngine
            from app.core.error_handler import ErrorHandler

            # Test initialization
            metrics = VibecodingMetrics()
            alerting = AlertingEngine()
            circuit_config = CircuitBreakerConfig(name="test")
            circuit_breaker = CircuitBreaker(circuit_config)
            recovery = AutoRecoveryEngine()
            error_handler = ErrorHandler()

            # Verify they are not None
            assert metrics is not None
            assert alerting is not None
            assert circuit_breaker is not None
            assert recovery is not None
            assert error_handler is not None

        except Exception as e:
            pytest.fail(f"Component initialization failed: {e}")

    def test_configuration_loading(self):
        """Test that configuration can be loaded"""
        try:
            from app.core.config import settings

            # Test that basic settings exist
            assert hasattr(settings, 'PROJECT_NAME')
            assert hasattr(settings, 'VERSION')
            assert hasattr(settings, 'API_V1_STR')

            # Test that settings have reasonable values
            assert settings.PROJECT_NAME == "Proyecto Semilla"
            assert settings.VERSION == "0.1.0"
            assert "/api/v1" in settings.API_V1_STR

        except Exception as e:
            pytest.fail(f"Configuration loading failed: {e}")

    def test_database_connection_config(self):
        """Test database connection configuration"""
        try:
            from app.core.config import settings

            # Check that database settings exist
            assert hasattr(settings, 'DATABASE_URL') or hasattr(settings, 'POSTGRES_SERVER')

            # If DATABASE_URL exists, it should be a string
            if hasattr(settings, 'DATABASE_URL'):
                assert isinstance(settings.DATABASE_URL, str)
                assert len(settings.DATABASE_URL) > 0

        except Exception as e:
            pytest.fail(f"Database configuration test failed: {e}")

    def test_security_settings(self):
        """Test security-related settings"""
        try:
            from app.core.config import settings

            # Check JWT settings
            assert hasattr(settings, 'SECRET_KEY')
            assert hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES')

            # Check that secret key exists and is not empty
            assert isinstance(settings.SECRET_KEY, str)
            assert len(settings.SECRET_KEY) > 0

            # Check token expiration is reasonable
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0

        except Exception as e:
            pytest.fail(f"Security settings test failed: {e}")

    def test_metrics_system_basic_functionality(self):
        """Test basic metrics system functionality"""
        try:
            from app.core.metrics import VibecodingMetrics

            metrics = VibecodingMetrics()

            # Test recording requests
            initial_count = metrics.request_count
            metrics.record_request(100.0, 200)

            assert metrics.request_count == initial_count + 1
            assert 100.0 in metrics.response_times

        except Exception as e:
            pytest.fail(f"Metrics system test failed: {e}")

    def test_alerting_system_basic_functionality(self):
        """Test basic alerting system functionality"""
        try:
            from app.core.alerting import AlertingEngine

            alerting = AlertingEngine()

            # Test that engine initializes
            assert alerting.alerts is not None
            assert alerting.rules is not None

            # Test getting active alerts (should be empty initially)
            active_alerts = alerting.get_active_alerts()
            assert isinstance(active_alerts, list)

        except Exception as e:
            pytest.fail(f"Alerting system test failed: {e}")

    def test_circuit_breaker_basic_functionality(self):
        """Test basic circuit breaker functionality"""
        try:
            from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

            config = CircuitBreakerConfig(name="integration_test")
            circuit_breaker = CircuitBreaker(config)

            # Test initial state
            assert circuit_breaker.state.value == "closed"
            assert circuit_breaker.failure_count == 0

            # Test successful function execution
            @circuit_breaker
            def test_function():
                return "success"

            result = test_function()
            assert result == "success"
            assert circuit_breaker.state.value == "closed"

        except Exception as e:
            pytest.fail(f"Circuit breaker test failed: {e}")

    def test_error_handler_basic_functionality(self):
        """Test basic error handler functionality"""
        try:
            from app.core.error_handler import ErrorHandler

            error_handler = ErrorHandler()

            # Test that handler initializes
            assert error_handler.fallback_responses is not None
            assert error_handler.error_counts is not None

            # Test error statistics
            stats = error_handler.get_error_statistics()
            assert isinstance(stats, dict)
            assert "error_counts" in stats

        except Exception as e:
            pytest.fail(f"Error handler test failed: {e}")

    def test_file_structure_integrity(self):
        """Test that critical files exist and are accessible"""
        import os
        from pathlib import Path

        critical_files = [
            "backend/app/main.py",
            "backend/app/core/config.py",
            "backend/app/core/database.py",
            "backend/app/core/security.py",
            "README.md",
            "requirements.txt"
        ]

        for file_path in critical_files:
            assert os.path.exists(file_path), f"Critical file missing: {file_path}"

    def test_package_structure(self):
        """Test that Python packages are properly structured"""
        import os

        # Check that __init__.py files exist where needed
        init_files = [
            "backend/app/__init__.py",
            "backend/app/core/__init__.py",
            "backend/app/api/__init__.py",
            "backend/app/models/__init__.py",
            "backend/app/schemas/__init__.py",
            "backend/app/services/__init__.py"
        ]

        for init_file in init_files:
            assert os.path.exists(init_file), f"Missing __init__.py: {init_file}"