"""
Security Policies and Compliance for Proyecto Semilla
GDPR, SOX, HIPAA compliance policies and data protection
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta


class ComplianceStandard(Enum):
    """Supported compliance standards"""
    GDPR = "gdpr"
    SOX = "sox"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    SOC2 = "soc2"


class DataSensitivity(Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    HIGHLY_SENSITIVE = "highly_sensitive"


class RetentionPolicy(Enum):
    """Data retention policies"""
    TEMPORARY = "temporary"  # 7 days
    SHORT_TERM = "short_term"  # 30 days
    MEDIUM_TERM = "medium_term"  # 90 days
    LONG_TERM = "long_term"  # 1 year
    PERMANENT = "permanent"  # Indefinite


@dataclass
class SecurityPolicy:
    """Security policy definition"""
    name: str
    description: str
    compliance_standards: List[ComplianceStandard]
    data_sensitivity: DataSensitivity
    retention_policy: RetentionPolicy
    encryption_required: bool
    audit_required: bool
    access_controls: List[str]
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


class SecurityPolicyManager:
    """
    Manager for security policies and compliance
    """

    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """Initialize default security policies"""

        # User data policy
        self.policies["user_personal_data"] = SecurityPolicy(
            name="User Personal Data",
            description="Policy for handling user personal information",
            compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA],
            data_sensitivity=DataSensitivity.HIGHLY_SENSITIVE,
            retention_policy=RetentionPolicy.PERMANENT,
            encryption_required=True,
            audit_required=True,
            access_controls=["gdpr_compliant", "data_protection_officer_approval"]
        )

        # Financial data policy
        self.policies["financial_data"] = SecurityPolicy(
            name="Financial Data",
            description="Policy for handling financial and payment information",
            compliance_standards=[ComplianceStandard.SOX, ComplianceStandard.PCI_DSS],
            data_sensitivity=DataSensitivity.RESTRICTED,
            retention_policy=RetentionPolicy.LONG_TERM,
            encryption_required=True,
            audit_required=True,
            access_controls=["sox_compliant", "finance_team_only"]
        )

        # Health data policy
        self.policies["health_data"] = SecurityPolicy(
            name="Health Data",
            description="Policy for handling health and medical information",
            compliance_standards=[ComplianceStandard.HIPAA],
            data_sensitivity=DataSensitivity.HIGHLY_SENSITIVE,
            retention_policy=RetentionPolicy.LONG_TERM,
            encryption_required=True,
            audit_required=True,
            access_controls=["hipaa_compliant", "medical_staff_only"]
        )

        # Audit logs policy
        self.policies["audit_logs"] = SecurityPolicy(
            name="Audit Logs",
            description="Policy for audit trail and security logs",
            compliance_standards=[ComplianceStandard.SOX, ComplianceStandard.ISO27001],
            data_sensitivity=DataSensitivity.CONFIDENTIAL,
            retention_policy=RetentionPolicy.LONG_TERM,
            encryption_required=False,
            audit_required=True,
            access_controls=["security_team_only", "read_only"]
        )

        # Analytics data policy
        self.policies["analytics_data"] = SecurityPolicy(
            name="Analytics Data",
            description="Policy for analytics and usage data",
            compliance_standards=[ComplianceStandard.GDPR],
            data_sensitivity=DataSensitivity.CONFIDENTIAL,
            retention_policy=RetentionPolicy.MEDIUM_TERM,
            encryption_required=False,
            audit_required=False,
            access_controls=["analytics_team_only", "aggregated_only"]
        )

    def get_policy(self, policy_name: str) -> Optional[SecurityPolicy]:
        """Get a security policy by name"""
        return self.policies.get(policy_name)

    def add_policy(self, policy: SecurityPolicy):
        """Add a new security policy"""
        self.policies[policy.name.lower().replace(" ", "_")] = policy

    def get_policies_by_compliance(self, standard: ComplianceStandard) -> List[SecurityPolicy]:
        """Get all policies that apply to a compliance standard"""
        return [policy for policy in self.policies.values() if standard in policy.compliance_standards]

    def get_policies_by_sensitivity(self, sensitivity: DataSensitivity) -> List[SecurityPolicy]:
        """Get all policies for a data sensitivity level"""
        return [policy for policy in self.policies.values() if policy.data_sensitivity == sensitivity]

    def validate_data_access(self, policy_name: str, user_permissions: List[str]) -> bool:
        """Validate if user has access to data under a policy"""
        policy = self.get_policy(policy_name)
        if not policy:
            return False

        # Check if user has all required access controls
        return all(permission in user_permissions for permission in policy.access_controls)

    def get_retention_period(self, policy_name: str) -> Optional[timedelta]:
        """Get retention period for a policy"""
        policy = self.get_policy(policy_name)
        if not policy:
            return None

        retention_map = {
            RetentionPolicy.TEMPORARY: timedelta(days=7),
            RetentionPolicy.SHORT_TERM: timedelta(days=30),
            RetentionPolicy.MEDIUM_TERM: timedelta(days=90),
            RetentionPolicy.LONG_TERM: timedelta(days=365),
            RetentionPolicy.PERMANENT: None
        }

        return retention_map.get(policy.retention_policy)


class DataEncryptionManager:
    """
    Manager for data encryption and key management
    """

    def __init__(self):
        self.encryption_keys: Dict[str, str] = {}
        self._load_encryption_keys()

    def _load_encryption_keys(self):
        """Load encryption keys from secure storage"""
        # In production, load from secure key management service
        import os
        self.encryption_keys = {
            "user_data": os.getenv("USER_DATA_ENCRYPTION_KEY", "default_user_key_32_chars_long"),
            "financial_data": os.getenv("FINANCIAL_DATA_ENCRYPTION_KEY", "default_financial_key_32_chars"),
            "health_data": os.getenv("HEALTH_DATA_ENCRYPTION_KEY", "default_health_key_32_chars_long")
        }

    def encrypt_sensitive_data(self, data: str, key_type: str = "user_data") -> str:
        """Encrypt sensitive data"""
        try:
            from cryptography.fernet import Fernet
            import base64

            key = self.encryption_keys.get(key_type, self.encryption_keys["user_data"])
            # Ensure key is 32 bytes
            key_bytes = key.encode()[:32].ljust(32, b'\0')
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            fernet = Fernet(fernet_key)

            return fernet.encrypt(data.encode()).decode()
        except Exception as e:
            # Log error but don't expose sensitive data
            print(f"Encryption error: {str(e)}")
            return data  # Return unencrypted as fallback

    def decrypt_sensitive_data(self, encrypted_data: str, key_type: str = "user_data") -> str:
        """Decrypt sensitive data"""
        try:
            from cryptography.fernet import Fernet
            import base64

            key = self.encryption_keys.get(key_type, self.encryption_keys["user_data"])
            key_bytes = key.encode()[:32].ljust(32, b'\0')
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            fernet = Fernet(fernet_key)

            return fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            # Log error but don't expose sensitive data
            print(f"Decryption error: {str(e)}")
            return encrypted_data  # Return encrypted as fallback


class ComplianceChecker:
    """
    Compliance validation and reporting
    """

    def __init__(self, policy_manager: SecurityPolicyManager):
        self.policy_manager = policy_manager

    def check_gdpr_compliance(self, data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check GDPR compliance for data handling"""
        issues = []

        # Check data minimization
        if "unnecessary_data" in data_handling:
            issues.append("Data minimization principle violated")

        # Check consent
        if not data_handling.get("user_consent", False):
            issues.append("User consent not obtained")

        # Check data retention
        retention_days = data_handling.get("retention_days", 0)
        if retention_days > 2555:  # 7 years max for GDPR
            issues.append("Data retention exceeds GDPR limits")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "recommendations": [
                "Implement data minimization practices",
                "Obtain explicit user consent",
                "Set appropriate data retention periods"
            ]
        }

    def check_hipaa_compliance(self, health_data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check HIPAA compliance for health data"""
        issues = []

        # Check encryption
        if not health_data_handling.get("encrypted", False):
            issues.append("Health data not encrypted at rest and in transit")

        # Check access controls
        if not health_data_handling.get("access_controls", False):
            issues.append("Inadequate access controls for PHI")

        # Check audit logging
        if not health_data_handling.get("audit_logging", False):
            issues.append("Audit logging not implemented for PHI access")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "recommendations": [
                "Encrypt all PHI data",
                "Implement role-based access controls",
                "Enable comprehensive audit logging"
            ]
        }

    def check_sox_compliance(self, financial_data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check SOX compliance for financial data"""
        issues = []

        # Check segregation of duties
        if not financial_data_handling.get("segregation_of_duties", False):
            issues.append("Segregation of duties not implemented")

        # Check audit trail
        if not financial_data_handling.get("audit_trail", False):
            issues.append("Complete audit trail not maintained")

        # Check access approval
        if not financial_data_handling.get("access_approval", False):
            issues.append("Access to financial systems not properly approved")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "recommendations": [
                "Implement segregation of duties",
                "Maintain complete audit trails",
                "Require approval for system access"
            ]
        }

    def generate_compliance_report(self, standard: ComplianceStandard) -> Dict[str, Any]:
        """Generate compliance report for a standard"""
        policies = self.policy_manager.get_policies_by_compliance(standard)

        report = {
            "standard": standard.value,
            "generated_at": datetime.utcnow().isoformat(),
            "policies_applicable": len(policies),
            "policies": []
        }

        for policy in policies:
            report["policies"].append({
                "name": policy.name,
                "description": policy.description,
                "data_sensitivity": policy.data_sensitivity.value,
                "encryption_required": policy.encryption_required,
                "audit_required": policy.audit_required
            })

        return report


# Global instances
security_policy_manager = SecurityPolicyManager()
data_encryption_manager = DataEncryptionManager()
compliance_checker = ComplianceChecker(security_policy_manager)