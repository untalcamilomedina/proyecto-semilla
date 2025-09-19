#!/usr/bin/env python3
"""
Security validation script for hardcoded users
This script validates that hardcoded users are handled securely
and detects potential security regressions
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Set
import json
import hashlib


class HardcodedUsersSecurityValidator:
    """Validates security aspects of hardcoded users implementation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []

    def log_issue(self, severity: str, category: str, message: str, file: str = None, line: int = None):
        """Log a security issue"""
        issue = {
            "severity": severity,
            "category": category,
            "message": message,
            "file": str(file) if file else None,
            "line": line
        }

        if severity == "CRITICAL" or severity == "HIGH":
            self.issues.append(issue)
        else:
            self.warnings.append(issue)

    def scan_for_hardcoded_credentials(self):
        """Scan codebase for hardcoded credentials"""
        print("🔍 Scanning for hardcoded credentials...")

        # Files to scan
        scan_files = [
            "*.py", "*.js", "*.ts", "*.jsx", "*.tsx",
            "*.env*", "*.sh", "*.yml", "*.yaml", "*.json",
            "*.md", "*.txt"
        ]

        hardcoded_patterns = [
            # Password patterns
            r"password.*=.*['\"](admin123|demo123|ChangeMeSecure123!)['\"]",
            r"['\"](admin123|demo123|ChangeMeSecure123!)['\"].*=.*password",

            # Email patterns in sensitive contexts
            r"NEXT_PUBLIC.*EMAIL.*=.*['\"](admin@proyectosemilla\.dev|demo@demo-company\.com|admin@example\.com)['\"]",
            r"NEXT_PUBLIC.*PASSWORD.*=.*['\"](admin123|demo123)['\"]",

            # Direct credential assignments
            r"email.*=.*['\"](admin@proyectosemilla\.dev|demo@demo-company\.com|admin@example\.com)['\"]",
            r"hashed_password.*=.*get_password_hash\(['\"](admin123|demo123)['\"]\)",
        ]

        found_issues = 0

        for pattern in scan_files:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file() and not self._should_skip_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')

                            for line_num, line in enumerate(lines, 1):
                                for cred_pattern in hardcoded_patterns:
                                    if re.search(cred_pattern, line, re.IGNORECASE):
                                        self.log_issue(
                                            "CRITICAL",
                                            "HARDCODED_CREDENTIALS",
                                            f"Found hardcoded credential pattern: {cred_pattern}",
                                            file_path,
                                            line_num
                                        )
                                        found_issues += 1

                    except Exception as e:
                        self.log_issue(
                            "LOW",
                            "FILE_READ_ERROR",
                            f"Could not read file {file_path}: {e}",
                            file_path
                        )

        print(f"✅ Credential scan completed. Found {found_issues} issues.")

    def validate_setup_status_logic(self):
        """Validate the setup status logic for security"""
        print("🔍 Validating setup status logic...")

        auth_file = self.project_root / "backend/app/api/v1/endpoints/auth.py"

        if not auth_file.exists():
            self.log_issue("HIGH", "MISSING_FILE", "Auth endpoints file not found", auth_file)
            return

        try:
            with open(auth_file, 'r') as f:
                content = f.read()

            # Check for hardcoded emails list
            hardcoded_emails_match = re.search(
                r'hardcoded_emails\s*=\s*\[(.*?)\]',
                content,
                re.DOTALL
            )

            if not hardcoded_emails_match:
                self.log_issue(
                    "HIGH",
                    "MISSING_VALIDATION",
                    "Hardcoded emails list not found in setup_status function",
                    auth_file
                )
                return

            emails_text = hardcoded_emails_match.group(1)

            # Extract individual emails
            email_pattern = r'["\']([^"\']+)["\']'
            found_emails = re.findall(email_pattern, emails_text)

            expected_emails = {
                "admin@proyectosemilla.dev",
                "demo@demo-company.com",
                "admin@example.com"
            }

            found_emails_set = set(found_emails)

            if found_emails_set != expected_emails:
                self.log_issue(
                    "MEDIUM",
                    "EMAIL_LIST_CHANGED",
                    f"Hardcoded emails list changed. Expected: {expected_emails}, Found: {found_emails_set}",
                    auth_file
                )

            # Check for proper exclusion logic
            if "not_in" not in content:
                self.log_issue(
                    "HIGH",
                    "MISSING_EXCLUSION",
                    "Setup status query does not exclude hardcoded users properly",
                    auth_file
                )

        except Exception as e:
            self.log_issue(
                "HIGH",
                "VALIDATION_ERROR",
                f"Could not validate setup status logic: {e}",
                auth_file
            )

    def check_environment_variable_security(self):
        """Check that environment variables are configured securely"""
        print("🔍 Checking environment variable security...")

        env_files = [
            self.project_root / ".env",
            self.project_root / ".env.example",
            self.project_root / ".env.local",
            self.project_root / "frontend" / ".env.local"
        ]

        for env_file in env_files:
            if env_file.exists():
                try:
                    with open(env_file, 'r') as f:
                        content = f.read()
                        lines = content.split('\n')

                        for line_num, line in enumerate(lines, 1):
                            line = line.strip()

                            # Check for insecure NEXT_PUBLIC variables
                            if line.startswith("NEXT_PUBLIC") and ("PASSWORD" in line or "SECRET" in line):
                                self.log_issue(
                                    "CRITICAL",
                                    "EXPOSED_SECRET",
                                    f"NEXT_PUBLIC variable contains sensitive data: {line.split('=')[0]}",
                                    env_file,
                                    line_num
                                )

                            # Check for default insecure passwords
                            if "PASSWORD" in line and any(insecure in line for insecure in ["admin123", "demo123", "password"]):
                                if not line.startswith("#"):  # Not a comment
                                    self.log_issue(
                                        "HIGH",
                                        "WEAK_PASSWORD",
                                        f"Environment file contains weak or default password: {line.split('=')[0]}",
                                        env_file,
                                        line_num
                                    )

                except Exception as e:
                    self.log_issue(
                        "LOW",
                        "FILE_READ_ERROR",
                        f"Could not read env file {env_file}: {e}",
                        env_file
                    )

    def validate_user_creation_scripts(self):
        """Validate that user creation scripts handle security properly"""
        print("🔍 Validating user creation scripts...")

        scripts_to_check = [
            self.project_root / "backend/app/initial_data.py",
            self.project_root / "backend/scripts/seed_data.py"
        ]

        for script in scripts_to_check:
            if script.exists():
                try:
                    with open(script, 'r') as f:
                        content = f.read()

                        # Check for hardcoded passwords
                        if "admin123" in content and "get_password_hash" in content:
                            # This is expected in initial_data.py, but should be flagged for review
                            self.log_issue(
                                "MEDIUM",
                                "HARDCODED_PASSWORD",
                                "Script contains hardcoded password that should be configurable",
                                script
                            )

                        # Check for environment variable usage
                        if "os.getenv" in content:
                            # Good - using environment variables
                            pass
                        elif "SEED_" in content:
                            # Check if environment variables are used properly
                            if "os.getenv" not in content:
                                self.log_issue(
                                    "MEDIUM",
                                    "MISSING_ENV_VAR",
                                    "Script references environment variables but doesn't use os.getenv",
                                    script
                                )

                except Exception as e:
                    self.log_issue(
                        "LOW",
                        "FILE_READ_ERROR",
                        f"Could not read script {script}: {e}",
                        script
                    )

    def check_file_permissions(self):
        """Check file permissions for sensitive files"""
        print("🔍 Checking file permissions...")

        sensitive_files = [
            ".env",
            ".env.local",
            "frontend/.env.local",
            "backend/scripts/seed_data.py",
            "backend/app/initial_data.py"
        ]

        for file_path_str in sensitive_files:
            file_path = self.project_root / file_path_str
            if file_path.exists():
                try:
                    import stat
                    st = file_path.stat()
                    mode = st.st_mode

                    # Check if file is world-readable
                    if mode & stat.S_IROTH:  # Others can read
                        self.log_issue(
                            "MEDIUM",
                            "INSECURE_PERMISSIONS",
                            f"File is world-readable: {file_path}",
                            file_path
                        )

                    # Check if file is group-readable (may be acceptable)
                    if mode & stat.S_IRGRP:  # Group can read
                        self.warnings.append({
                            "severity": "LOW",
                            "category": "PERMISSIONS",
                            "message": f"File is group-readable: {file_path}",
                            "file": str(file_path)
                        })

                except Exception as e:
                    self.log_issue(
                        "LOW",
                        "PERMISSION_CHECK_ERROR",
                        f"Could not check permissions for {file_path}: {e}",
                        file_path
                    )

    def generate_security_report(self) -> Dict:
        """Generate a comprehensive security report"""
        print("📊 Generating security report...")

        report = {
            "summary": {
                "total_issues": len(self.issues),
                "total_warnings": len(self.warnings),
                "scan_timestamp": str(self.project_root),
                "project_root": str(self.project_root)
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []

        if any(issue["category"] == "HARDCODED_CREDENTIALS" for issue in self.issues):
            recommendations.append(
                "Remove all hardcoded credentials from source code and configuration files"
            )

        if any(issue["category"] == "EXPOSED_SECRET" for issue in self.issues):
            recommendations.append(
                "Never expose secrets or passwords in NEXT_PUBLIC environment variables"
            )

        if any(issue["category"] == "WEAK_PASSWORD" for issue in self.issues):
            recommendations.append(
                "Use strong, unique passwords and avoid default values in production"
            )

        if any(issue["category"] == "MISSING_ENV_VAR" for issue in self.issues):
            recommendations.append(
                "Use environment variables for all configuration that varies by environment"
            )

        if any(issue["category"] == "INSECURE_PERMISSIONS" for issue in self.issues):
            recommendations.append(
                "Restrict file permissions for sensitive configuration files"
            )

        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "Regular security audits of hardcoded user implementations",
                "Implement automated security testing in CI/CD pipeline",
                "Document security requirements for future development",
                "Monitor for unauthorized access attempts to hardcoded accounts"
            ])

        return recommendations

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped during scanning"""
        # Skip common non-source files
        skip_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            "*.pyc",
            "*.pyo",
            "*.log",
            "coverage.xml",
            ".coverage"
        ]

        file_str = str(file_path)

        for pattern in skip_patterns:
            if pattern in file_str:
                return True

        # Skip files larger than 10MB
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return True
        except:
            pass

        return False

    def run_validation(self) -> Dict:
        """Run all security validations"""
        print("🚀 Starting hardcoded users security validation...")
        print(f"📁 Project root: {self.project_root}")
        print("=" * 60)

        # Run all validation checks
        self.scan_for_hardcoded_credentials()
        self.validate_setup_status_logic()
        self.check_environment_variable_security()
        self.validate_user_creation_scripts()
        self.check_file_permissions()

        # Generate report
        report = self.generate_security_report()

        return report


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    validator = HardcodedUsersSecurityValidator(project_root)
    report = validator.run_validation()

    # Print summary
    print("\n" + "=" * 60)
    print("📋 SECURITY VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Issues: {report['summary']['total_issues']}")
    print(f"Total Warnings: {report['summary']['total_warnings']}")

    # Print issues
    if report["issues"]:
        print("\n❌ ISSUES FOUND:")
        for issue in report["issues"]:
            severity_icon = "🔴" if issue["severity"] == "CRITICAL" else "🟠"
            print(f"{severity_icon} {issue['severity']}: {issue['message']}")
            if issue["file"]:
                location = f"{issue['file']}"
                if issue["line"]:
                    location += f":{issue['line']}"
                print(f"   📍 Location: {location}")

    # Print warnings
    if report["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in report["warnings"]:
            print(f"🟡 {warning['severity']}: {warning['message']}")
            if warning["file"]:
                location = f"{warning['file']}"
                if warning["line"]:
                    location += f":{warning['line']}"
                print(f"   📍 Location: {location}")

    # Print recommendations
    if report["recommendations"]:
        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")

    # Exit with appropriate code
    if report["summary"]["total_issues"] > 0:
        print("\n❌ Security validation FAILED - Issues must be addressed")
        sys.exit(1)
    else:
        print("\n✅ Security validation PASSED")
        if report["summary"]["total_warnings"] > 0:
            print("⚠️  Review warnings for potential improvements")
        sys.exit(0)


if __name__ == "__main__":
    main()