"""
Tests for Security Policies and Compliance
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.security_policies import (
    SecurityPolicyManager,
    DataEncryptionManager,
    ComplianceChecker,
    ComplianceStandard,
    DataSensitivity,
    RetentionPolicy
)


class TestSecurityPolicyManager:
    """Test Security Policy Manager"""

    def setup_method(self):
        self.manager = SecurityPolicyManager()

    def test_default_policies_loaded(self):
        """Test that default policies are loaded"""
        assert len(self.manager.policies) > 0
        assert "user_personal_data" in self.manager.policies
        assert "financial_data" in self.manager.policies
        assert "health_data" in self.manager.policies

    def test_get_policy(self):
        """Test getting a policy by name"""
        policy = self.manager.get_policy("user_personal_data")
        assert policy is not None
        assert policy.data_sensitivity == DataSensitivity.HIGHLY_SENSITIVE
        assert ComplianceStandard.GDPR in policy.compliance_standards

    def test_get_policies_by_compliance(self):
        """Test getting policies by compliance standard"""
        gdpr_policies = self.manager.get_policies_by_compliance(ComplianceStandard.GDPR)
        assert len(gdpr_policies) > 0

        hipaa_policies = self.manager.get_policies_by_compliance(ComplianceStandard.HIPAA)
        assert len(hipaa_policies) > 0

    def test_validate_data_access(self):
        """Test data access validation"""
        user_permissions = ["gdpr_compliant", "data_protection_officer_approval"]

        # Should allow access
        assert self.manager.validate_data_access("user_personal_data", user_permissions)

        # Should deny access
        insufficient_permissions = ["basic_user"]
        assert not self.manager.validate_data_access("user_personal_data", insufficient_permissions)


class TestDataEncryptionManager:
    """Test Data Encryption Manager"""

    def setup_method(self):
        self.manager = DataEncryptionManager()

    def test_encryption_keys_loaded(self):
        """Test that encryption keys are loaded"""
        assert len(self.manager.encryption_keys) > 0
        assert "user_data" in self.manager.encryption_keys

    def test_encrypt_decrypt_cycle(self):
        """Test full encrypt/decrypt cycle"""
        test_data = "sensitive information"

        encrypted = self.manager.encrypt_sensitive_data(test_data, "user_data")
        assert encrypted != test_data
        assert encrypted.startswith('gAAAAA')  # Fernet prefix

        decrypted = self.manager.decrypt_sensitive_data(encrypted, "user_data")
        assert decrypted == test_data


class TestComplianceChecker:
    """Test Compliance Checker"""

    def setup_method(self):
        policy_manager = SecurityPolicyManager()
        self.checker = ComplianceChecker(policy_manager)

    @pytest.mark.asyncio
    async def test_gdpr_compliance_check(self):
        """Test GDPR compliance checking"""
        data_handling = {
            "user_consent": True,
            "retention_days": 200
        }

        result = self.checker.check_gdpr_compliance(data_handling)
        assert "compliant" in result
        assert "issues" in result

    @pytest.mark.asyncio
    async def test_hipaa_compliance_check(self):
        """Test HIPAA compliance checking"""
        data_handling = {
            "encrypted": True,
            "access_controls": True,
            "audit_logging": True
        }

        result = self.checker.check_hipaa_compliance(data_handling)
        assert result["compliant"] is True

    @pytest.mark.asyncio
    async def test_sox_compliance_check(self):
        """Test SOX compliance checking"""
        data_handling = {
            "segregation_of_duties": True,
            "audit_trail": True,
            "access_approval": True
        }

        result = self.checker.check_sox_compliance(data_handling)
        assert result["compliant"] is True

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self):
        """Test compliance report generation"""
        report = await self.checker.generate_compliance_report(ComplianceStandard.GDPR)
        assert "standard" in report
        assert "policies_applicable" in report
        assert report["standard"] == "gdpr"


class TestSecurityHeaders:
    """Test Security Headers Middleware"""

    @pytest.mark.asyncio
    async def test_security_headers_middleware(self):
        """Test security headers middleware"""
        from app.middleware.security_headers import SecurityHeadersMiddleware
        from fastapi import Request, Response
        from fastapi.responses import JSONResponse

        middleware = SecurityHeadersMiddleware(None)

        # Create mock request and response
        request = Request(scope={"type": "http", "method": "GET", "path": "/"})
        response = JSONResponse(content={"test": "data"})

        # Process through middleware
        result = await middleware.dispatch(request, lambda: response)

        # Check security headers are present
        assert "Content-Security-Policy" in result.headers
        assert "Strict-Transport-Security" in result.headers
        assert "X-Frame-Options" in result.headers
        assert "X-Content-Type-Options" in result.headers
        assert "X-XSS-Protection" in result.headers


class TestEncryptedFields:
    """Test Encrypted Fields functionality"""

    def test_encrypt_field_value(self):
        """Test field value encryption utility"""
        from app.core.encrypted_fields import encrypt_field_value, decrypt_field_value

        test_value = "secret data"
        encrypted = encrypt_field_value(test_value, "user_data")
        assert encrypted != test_value

        decrypted = decrypt_field_value(encrypted, "user_data")
        assert decrypted == test_value

    def test_encrypt_dict_value(self):
        """Test encrypting dictionary values"""
        from app.core.encrypted_fields import encrypt_field_value, decrypt_field_value

        test_dict = {"key": "value", "number": 42}
        encrypted = encrypt_field_value(test_dict, "user_data")
        assert encrypted != str(test_dict)

        decrypted = decrypt_field_value(encrypted, "user_data")
        assert decrypted == test_dict


class TestAlertingSystem:
    """Test Security Alerting System"""

    def setup_method(self):
        from app.core.alerting import AlertingEngine
        self.engine = AlertingEngine()

    def test_default_rules_loaded(self):
        """Test that default alerting rules are loaded"""
        assert len(self.engine.rules) > 0
        assert "failed_login_attempts_per_hour_above_10" in self.engine.rules

    def test_add_custom_rule(self):
        """Test adding custom alert rule"""
        from app.core.alerting import AlertRule

        custom_rule = AlertRule(
            metric="custom_metric",
            threshold=100,
            condition="above",
            severity="medium",
            description="Custom alert rule"
        )

        self.engine.add_rule(custom_rule)
        assert "custom_metric_above_100" in self.engine.rules

    @pytest.mark.asyncio
    async def test_check_alerts(self):
        """Test alert checking"""
        metrics = {
            "response_time_p95": 600,  # Above threshold
            "error_rate_percentage": 2  # Below threshold
        }

        await self.engine.check_alerts(metrics)

        # Should have triggered alert for response time
        active_alerts = self.engine.get_active_alerts()
        assert len(active_alerts) > 0

        alert_metrics = [alert["metric"] for alert in active_alerts]
        assert "response_time_p95" in alert_metrics