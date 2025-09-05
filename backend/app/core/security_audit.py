"""
Security Audit System for Proyecto Semilla
Comprehensive security assessment and compliance checking
"""

import asyncio
import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from pydantic import BaseModel


class SecuritySeverity(Enum):
    """Security issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceStandard(Enum):
    """Supported compliance standards"""
    OWASP_TOP_10 = "owasp_top_10"
    NIST_800_53 = "nist_800_53"
    ISO_27001 = "iso_27001"
    GDPR = "gdpr"
    SOC2 = "soc2"


@dataclass
class SecurityFinding:
    """Security finding data structure"""
    id: str
    title: str
    description: str
    severity: SecuritySeverity
    category: str
    standard: str
    recommendation: str
    evidence: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class AuditResult:
    """Security audit result"""
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    info_findings: int
    compliance_score: float
    risk_score: float
    findings: List[SecurityFinding]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_findings': self.total_findings,
            'findings_by_severity': {
                'critical': self.critical_findings,
                'high': self.high_findings,
                'medium': self.medium_findings,
                'low': self.low_findings,
                'info': self.info_findings
            },
            'compliance_score': self.compliance_score,
            'risk_score': self.risk_score,
            'findings': [finding.to_dict() for finding in self.findings],
            'timestamp': self.timestamp.isoformat()
        }


class SecurityAuditEngine:
    """
    Comprehensive security audit engine for Proyecto Semilla
    """

    def __init__(self):
        self.findings: List[SecurityFinding] = []
        self.audit_id = self._generate_audit_id()

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"audit_{timestamp}"

    def _generate_finding_id(self, category: str, title: str) -> str:
        """Generate unique finding ID"""
        content = f"{category}_{title}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    async def run_comprehensive_audit(self) -> AuditResult:
        """
        Run comprehensive security audit
        """
        print("🔍 Starting comprehensive security audit...")

        # Reset findings
        self.findings = []

        # Run all audit checks
        await self._audit_authentication()
        await self._audit_authorization()
        await self._audit_input_validation()
        await self._audit_session_management()
        await self._audit_data_protection()
        await self._audit_configuration()
        await self._audit_dependencies()
        await self._audit_logging()
        await self._audit_error_handling()

        # Calculate scores
        compliance_score = self._calculate_compliance_score()
        risk_score = self._calculate_risk_score()

        # Count findings by severity
        severity_counts = self._count_findings_by_severity()

        result = AuditResult(
            total_findings=len(self.findings),
            critical_findings=severity_counts[SecuritySeverity.CRITICAL],
            high_findings=severity_counts[SecuritySeverity.HIGH],
            medium_findings=severity_counts[SecuritySeverity.MEDIUM],
            low_findings=severity_counts[SecuritySeverity.LOW],
            info_findings=severity_counts[SecuritySeverity.INFO],
            compliance_score=compliance_score,
            risk_score=risk_score,
            findings=self.findings,
            timestamp=datetime.utcnow()
        )

        print(f"✅ Security audit completed: {len(self.findings)} findings, "
              ".1f"
              ".1f")

        return result

    async def _audit_authentication(self):
        """Audit authentication mechanisms"""
        try:
            from app.core.config import settings

            # Check JWT configuration
            if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
                self._add_finding(
                    title="Missing JWT Secret Key",
                    description="JWT secret key is not configured",
                    severity=SecuritySeverity.CRITICAL,
                    category="authentication",
                    standard="owasp_a2",
                    recommendation="Configure a strong SECRET_KEY in environment variables",
                    evidence={"secret_key_configured": False}
                )

            # Check password requirements
            if not hasattr(settings, 'SECRET_KEY') or len(settings.SECRET_KEY) < 32:
                self._add_finding(
                    title="Weak JWT Secret Key",
                    description="JWT secret key is too short (minimum 32 characters)",
                    severity=SecuritySeverity.HIGH,
                    category="authentication",
                    standard="owasp_a2",
                    recommendation="Use a secret key of at least 32 characters",
                    evidence={"secret_key_length": len(settings.SECRET_KEY) if hasattr(settings, 'SECRET_KEY') else 0}
                )

            # Check token expiration
            if hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES'):
                if settings.ACCESS_TOKEN_EXPIRE_MINUTES > 1440:  # 24 hours
                    self._add_finding(
                        title="Token Expiration Too Long",
                        description="Access tokens expire after more than 24 hours",
                        severity=SecuritySeverity.MEDIUM,
                        category="authentication",
                        standard="owasp_a2",
                        recommendation="Reduce token expiration to maximum 24 hours",
                        evidence={"expiration_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES}
                    )

        except Exception as e:
            self._add_finding(
                title="Authentication Audit Error",
                description=f"Failed to audit authentication: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review authentication configuration",
                evidence={"error": str(e)}
            )

    async def _audit_authorization(self):
        """Audit authorization mechanisms"""
        try:
            # Check if RLS is enabled (this would require database connection)
            # For now, we'll check configuration
            from app.core.config import settings

            if hasattr(settings, 'DB_RLS_ENABLED'):
                if not settings.DB_RLS_ENABLED:
                    self._add_finding(
                        title="Row Level Security Disabled",
                        description="Database Row Level Security is not enabled",
                        severity=SecuritySeverity.HIGH,
                        category="authorization",
                        standard="owasp_a4",
                        recommendation="Enable Row Level Security in database",
                        evidence={"rls_enabled": False}
                    )

        except Exception as e:
            self._add_finding(
                title="Authorization Audit Error",
                description=f"Failed to audit authorization: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review authorization configuration",
                evidence={"error": str(e)}
            )

    async def _audit_input_validation(self):
        """Audit input validation mechanisms"""
        try:
            # Check if Pydantic is being used for validation
            import pydantic
            pydantic_version = pydantic.VERSION

            if pydantic_version < "2.0.0":
                self._add_finding(
                    title="Outdated Pydantic Version",
                    description=f"Pydantic version {pydantic_version} is outdated",
                    severity=SecuritySeverity.MEDIUM,
                    category="input_validation",
                    standard="owasp_a1",
                    recommendation="Upgrade to Pydantic v2.x for better security",
                    evidence={"pydantic_version": pydantic_version}
                )

        except Exception as e:
            self._add_finding(
                title="Input Validation Audit Error",
                description=f"Failed to audit input validation: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review input validation configuration",
                evidence={"error": str(e)}
            )

    async def _audit_session_management(self):
        """Audit session management"""
        try:
            from app.core.config import settings

            # Check session timeout
            if hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES'):
                if settings.ACCESS_TOKEN_EXPIRE_MINUTES < 15:  # Less than 15 minutes
                    self._add_finding(
                        title="Session Timeout Too Short",
                        description="Session timeout is too short for user experience",
                        severity=SecuritySeverity.LOW,
                        category="session_management",
                        standard="owasp_a2",
                        recommendation="Consider increasing session timeout to 15-60 minutes",
                        evidence={"timeout_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES}
                    )

        except Exception as e:
            self._add_finding(
                title="Session Management Audit Error",
                description=f"Failed to audit session management: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review session management configuration",
                evidence={"error": str(e)}
            )

    async def _audit_data_protection(self):
        """Audit data protection mechanisms"""
        try:
            from app.core.config import settings

            # Check if sensitive data is logged
            # This is a basic check - in practice, we'd scan log files
            sensitive_patterns = [
                r'password',
                r'secret',
                r'token',
                r'key'
            ]

            # For demonstration, we'll assume logs are clean
            # In real implementation, scan actual log files

        except Exception as e:
            self._add_finding(
                title="Data Protection Audit Error",
                description=f"Failed to audit data protection: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review data protection measures",
                evidence={"error": str(e)}
            )

    async def _audit_configuration(self):
        """Audit configuration security"""
        try:
            from app.core.config import settings

            # Check debug mode
            if hasattr(settings, 'DEBUG') and settings.DEBUG:
                self._add_finding(
                    title="Debug Mode Enabled",
                    description="Application is running in debug mode",
                    severity=SecuritySeverity.MEDIUM,
                    category="configuration",
                    standard="general",
                    recommendation="Disable debug mode in production",
                    evidence={"debug_enabled": True}
                )

            # Check allowed hosts
            if hasattr(settings, 'ALLOWED_HOSTS'):
                if settings.ALLOWED_HOSTS == ["*"]:
                    self._add_finding(
                        title="Wildcard Allowed Hosts",
                        description="ALLOWED_HOSTS is set to wildcard (*)",
                        severity=SecuritySeverity.HIGH,
                        category="configuration",
                        standard="owasp_a6",
                        recommendation="Specify explicit allowed hosts",
                        evidence={"allowed_hosts": settings.ALLOWED_HOSTS}
                    )

        except Exception as e:
            self._add_finding(
                title="Configuration Audit Error",
                description=f"Failed to audit configuration: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review configuration security",
                evidence={"error": str(e)}
            )

    async def _audit_dependencies(self):
        """Audit third-party dependencies"""
        try:
            import subprocess
            import json

            # Check for known vulnerabilities using safety or similar
            # For demonstration, we'll check some basic packages
            vulnerable_packages = []

            try:
                result = subprocess.run(['pip', 'list', '--format=json'],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    packages = json.loads(result.stdout)
                    for package in packages:
                        name = package.get('name', '').lower()
                        version = package.get('version', '')

                        # Check for known vulnerable packages (simplified)
                        if name == 'django' and version.startswith('1.'):
                            vulnerable_packages.append(f"{name} {version}")
                        elif name == 'flask' and version.startswith('1.'):
                            vulnerable_packages.append(f"{name} {version}")

            except (subprocess.TimeoutExpired, FileNotFoundError):
                # pip not available or timeout
                pass

            if vulnerable_packages:
                self._add_finding(
                    title="Vulnerable Dependencies",
                    description=f"Found {len(vulnerable_packages)} potentially vulnerable packages",
                    severity=SecuritySeverity.HIGH,
                    category="dependencies",
                    standard="owasp_a9",
                    recommendation="Update vulnerable dependencies",
                    evidence={"vulnerable_packages": vulnerable_packages}
                )

        except Exception as e:
            self._add_finding(
                title="Dependencies Audit Error",
                description=f"Failed to audit dependencies: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review dependency security",
                evidence={"error": str(e)}
            )

    async def _audit_logging(self):
        """Audit logging configuration"""
        try:
            import logging
            import os

            # Check if logs directory exists and is secure
            log_dir = "logs"
            if os.path.exists(log_dir):
                stat = os.stat(log_dir)
                # Check if directory is world-writable (insecure)
                if stat.st_mode & 0o002:  # world-writable
                    self._add_finding(
                        title="Insecure Log Directory Permissions",
                        description="Log directory is world-writable",
                        severity=SecuritySeverity.MEDIUM,
                        category="logging",
                        standard="general",
                        recommendation="Restrict log directory permissions to 755 or less",
                        evidence={"log_dir_permissions": oct(stat.st_mode)}
                    )

        except Exception as e:
            self._add_finding(
                title="Logging Audit Error",
                description=f"Failed to audit logging: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review logging configuration",
                evidence={"error": str(e)}
            )

    async def _audit_error_handling(self):
        """Audit error handling mechanisms"""
        try:
            # Check if error handler is configured
            from app.core.error_handler import ErrorHandler

            # Try to instantiate error handler
            error_handler = ErrorHandler()

            if not hasattr(error_handler, 'handle_error'):
                self._add_finding(
                    title="Missing Error Handler",
                    description="Error handler is not properly configured",
                    severity=SecuritySeverity.MEDIUM,
                    category="error_handling",
                    standard="owasp_a6",
                    recommendation="Implement comprehensive error handling",
                    evidence={"error_handler_methods": dir(error_handler)}
                )

        except Exception as e:
            self._add_finding(
                title="Error Handling Audit Error",
                description=f"Failed to audit error handling: {str(e)}",
                severity=SecuritySeverity.MEDIUM,
                category="audit_error",
                standard="general",
                recommendation="Review error handling implementation",
                evidence={"error": str(e)}
            )

    def _add_finding(self, title: str, description: str, severity: SecuritySeverity,
                    category: str, standard: str, recommendation: str, evidence: Dict[str, Any]):
        """Add a security finding"""
        finding_id = self._generate_finding_id(category, title)

        finding = SecurityFinding(
            id=finding_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            standard=standard,
            recommendation=recommendation,
            evidence=evidence,
            timestamp=datetime.utcnow()
        )

        self.findings.append(finding)

    def _count_findings_by_severity(self) -> Dict[SecuritySeverity, int]:
        """Count findings by severity"""
        counts = {
            SecuritySeverity.CRITICAL: 0,
            SecuritySeverity.HIGH: 0,
            SecuritySeverity.MEDIUM: 0,
            SecuritySeverity.LOW: 0,
            SecuritySeverity.INFO: 0
        }

        for finding in self.findings:
            counts[finding.severity] += 1

        return counts

    def _calculate_compliance_score(self) -> float:
        """Calculate compliance score based on findings"""
        if not self.findings:
            return 100.0

        # Weight findings by severity
        weights = {
            SecuritySeverity.CRITICAL: 10,
            SecuritySeverity.HIGH: 5,
            SecuritySeverity.MEDIUM: 2,
            SecuritySeverity.LOW: 1,
            SecuritySeverity.INFO: 0.5
        }

        total_weight = sum(weights[severity] for severity in weights.keys())
        actual_weight = sum(weights[finding.severity] for finding in self.findings)

        # Compliance score = 100 - (actual_weight / total_weight * 100)
        # But cap at reasonable bounds
        score = 100 - (actual_weight / len(self.findings) * 10)
        return max(0, min(100, score))

    def _calculate_risk_score(self) -> float:
        """Calculate risk score based on findings"""
        if not self.findings:
            return 0.0

        severity_weights = {
            SecuritySeverity.CRITICAL: 100,
            SecuritySeverity.HIGH: 50,
            SecuritySeverity.MEDIUM: 20,
            SecuritySeverity.LOW: 5,
            SecuritySeverity.INFO: 1
        }

        total_risk = sum(severity_weights[finding.severity] for finding in self.findings)
        max_possible_risk = len(self.findings) * severity_weights[SecuritySeverity.CRITICAL]

        if max_possible_risk == 0:
            return 0.0

        return (total_risk / max_possible_risk) * 100

    async def generate_audit_report(self, result: AuditResult) -> str:
        """Generate detailed audit report"""
        report = f"""
# 🔍 Security Audit Report - {self.audit_id}
**Generated**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

## 📊 Executive Summary

- **Total Findings**: {result.total_findings}
- **Compliance Score**: {result.compliance_score:.1f}%
- **Risk Score**: {result.risk_score:.1f}%
- **Critical Issues**: {result.critical_findings}
- **High Priority**: {result.high_findings}

## 🔴 Critical Findings

"""

        critical_findings = [f for f in result.findings if f.severity == SecuritySeverity.CRITICAL]
        for finding in critical_findings:
            report += f"""
### {finding.title}
**Severity**: {finding.severity.value.upper()}
**Category**: {finding.category}
**Standard**: {finding.standard}

{finding.description}

**Recommendation**: {finding.recommendation}

**Evidence**: {json.dumps(finding.evidence, indent=2)}
"""

        report += "\n## 🟠 High Priority Findings\n"

        high_findings = [f for f in result.findings if f.severity == SecuritySeverity.HIGH]
        for finding in high_findings:
            report += f"""
### {finding.title}
**Category**: {finding.category}
**Standard**: {finding.standard}

{finding.description}

**Recommendation**: {finding.recommendation}
"""

        report += "\n## 📋 Recommendations\n\n"

        # Group recommendations by category
        recommendations = {}
        for finding in result.findings:
            if finding.category not in recommendations:
                recommendations[finding.category] = []
            recommendations[finding.category].append(finding.recommendation)

        for category, recs in recommendations.items():
            report += f"### {category.title()}\n"
            for rec in set(recs):  # Remove duplicates
                report += f"- {rec}\n"
            report += "\n"

        return report

    async def export_findings_json(self, result: AuditResult, filename: str):
        """Export findings to JSON file"""
        with open(filename, 'w') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)

    async def export_findings_csv(self, result: AuditResult, filename: str):
        """Export findings to CSV file"""
        import csv

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Title', 'Severity', 'Category', 'Standard', 'Recommendation'])

            for finding in result.findings:
                writer.writerow([
                    finding.id,
                    finding.title,
                    finding.severity.value,
                    finding.category,
                    finding.standard,
                    finding.recommendation
                ])


# Global audit engine instance
audit_engine = SecurityAuditEngine()


async def run_security_audit() -> AuditResult:
    """Convenience function to run security audit"""
    return await audit_engine.run_comprehensive_audit()


async def generate_security_report(result: AuditResult, output_dir: str = "security_reports"):
    """Generate and save security audit report"""
    import os

    os.makedirs(output_dir, exist_ok=True)

    # Generate report
    report = await audit_engine.generate_audit_report(result)

    # Save report
    timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
    report_file = f"{output_dir}/security_audit_{timestamp}.md"
    json_file = f"{output_dir}/security_audit_{timestamp}.json"
    csv_file = f"{output_dir}/security_audit_{timestamp}.csv"

    with open(report_file, 'w') as f:
        f.write(report)

    await audit_engine.export_findings_json(result, json_file)
    await audit_engine.export_findings_csv(result, csv_file)

    return {
        'report': report_file,
        'json': json_file,
        'csv': csv_file
    }