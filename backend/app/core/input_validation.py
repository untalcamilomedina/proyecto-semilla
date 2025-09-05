"""
Enterprise Input Validation System for Proyecto Semilla
Comprehensive validation with sanitization and security checks
"""

import re
import hashlib
import unicodedata
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, validator, ValidationError
from email_validator import validate_email, EmailNotValidError


class ValidationSeverity(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class InputType(Enum):
    """Supported input types"""
    STRING = "string"
    EMAIL = "email"
    PASSWORD = "password"
    URL = "url"
    JSON = "json"
    NUMERIC = "numeric"
    DATE = "date"
    FILE = "file"


@dataclass
class ValidationRule:
    """Validation rule configuration"""
    rule_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    severity: ValidationSeverity = ValidationSeverity.ERROR
    message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    value: Any
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SanitizationResult:
    """Result of input sanitization"""
    original_value: Any
    sanitized_value: Any
    changes_made: List[str] = field(default_factory=list)
    security_flags: List[str] = field(default_factory=list)


class EnterpriseValidator:
    """
    Enterprise-grade input validation and sanitization
    """

    def __init__(self):
        self.custom_validators: Dict[str, Callable] = {}
        self.sanitizers: Dict[str, Callable] = {}

        # Initialize built-in validators and sanitizers
        self._initialize_validators()
        self._initialize_sanitizers()

    def _initialize_validators(self):
        """Initialize built-in validators"""
        self.custom_validators.update({
            'string': self._validate_string,
            'email': self._validate_email,
            'password': self._validate_password,
            'url': self._validate_url,
            'numeric': self._validate_numeric,
            'date': self._validate_date,
            'json': self._validate_json,
            'file': self._validate_file
        })

    def _initialize_sanitizers(self):
        """Initialize built-in sanitizers"""
        self.sanitizers.update({
            'sql_injection': self._sanitize_sql_injection,
            'xss': self._sanitize_xss,
            'command_injection': self._sanitize_command_injection,
            'path_traversal': self._sanitize_path_traversal,
            'html_encoding': self._encode_html_entities,
            'unicode_normalize': self._normalize_unicode
        })

    async def validate_input(self, input_type: Union[str, InputType],
                           value: Any, rules: Optional[List[ValidationRule]] = None) -> ValidationResult:
        """
        Validate input with comprehensive checks
        """
        if isinstance(input_type, InputType):
            input_type = input_type.value

        # Get validator
        validator = self.custom_validators.get(input_type)
        if not validator:
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=[f"No validator found for type: {input_type}"]
            )

        # Apply validation
        try:
            result = await validator(value, rules or [])
            return result
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=[f"Validation error: {str(e)}"]
            )

    async def sanitize_input(self, value: Any, sanitizers: List[str]) -> SanitizationResult:
        """
        Sanitize input using multiple sanitization methods
        """
        original_value = value
        current_value = value
        changes_made = []
        security_flags = []

        for sanitizer_name in sanitizers:
            sanitizer = self.sanitizers.get(sanitizer_name)
            if sanitizer:
                try:
                    sanitized, changes, flags = await sanitizer(current_value)
                    if sanitized != current_value:
                        changes_made.extend(changes)
                        security_flags.extend(flags)
                        current_value = sanitized
                except Exception as e:
                    security_flags.append(f"Sanitization error in {sanitizer_name}: {str(e)}")

        return SanitizationResult(
            original_value=original_value,
            sanitized_value=current_value,
            changes_made=changes_made,
            security_flags=security_flags
        )

    async def validate_and_sanitize(self, input_type: Union[str, InputType],
                                  value: Any, rules: Optional[List[ValidationRule]] = None,
                                  sanitizers: Optional[List[str]] = None) -> ValidationResult:
        """
        Validate and sanitize input in one operation
        """
        # First sanitize if requested
        if sanitizers:
            sanitization_result = await self.sanitize_input(value, sanitizers)
            value = sanitization_result.sanitized_value

        # Then validate
        validation_result = await self.validate_input(input_type, value, rules)

        # Combine results
        if sanitization_result:
            validation_result.sanitized_value = sanitization_result.sanitized_value
            validation_result.metadata.update({
                'sanitization_changes': sanitization_result.changes_made,
                'security_flags': sanitization_result.security_flags
            })

        return validation_result

    # Built-in validators
    async def _validate_string(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate string input"""
        errors = []
        warnings = []

        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["Value must be a string"]
            )

        # Apply rules
        for rule in rules:
            if rule.rule_type == 'length':
                min_len = rule.parameters.get('min', 0)
                max_len = rule.parameters.get('max', float('inf'))

                if len(value) < min_len:
                    errors.append(f"String too short (minimum {min_len} characters)")
                elif len(value) > max_len:
                    errors.append(f"String too long (maximum {max_len} characters)")

            elif rule.rule_type == 'pattern':
                pattern = rule.parameters.get('pattern')
                if pattern and not re.match(pattern, value):
                    errors.append(rule.message or f"String does not match required pattern")

            elif rule.rule_type == 'not_empty':
                if not value.strip():
                    errors.append("String cannot be empty or whitespace only")

            elif rule.rule_type == 'no_special_chars':
                if re.search(r'[^\w\s-]', value):
                    warnings.append("String contains special characters")

        return ValidationResult(
            is_valid=len(errors) == 0,
            value=value,
            errors=errors,
            warnings=warnings
        )

    async def _validate_email(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate email input"""
        errors = []

        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["Email must be a string"]
            )

        try:
            # Use email-validator library for comprehensive validation
            validated = validate_email(value, check_deliverability=False)
            normalized_email = validated.email

            return ValidationResult(
                is_valid=True,
                value=value,
                sanitized_value=normalized_email,
                metadata={'normalized_email': normalized_email}
            )

        except EmailNotValidError as e:
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=[f"Invalid email format: {str(e)}"]
            )

    async def _validate_password(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate password input"""
        errors = []
        warnings = []

        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["Password must be a string"]
            )

        # Default password requirements
        min_length = 8
        require_uppercase = True
        require_lowercase = True
        require_digits = True
        require_special = False

        # Apply custom rules
        for rule in rules:
            if rule.rule_type == 'min_length':
                min_length = rule.parameters.get('length', min_length)
            elif rule.rule_type == 'require_uppercase':
                require_uppercase = rule.parameters.get('required', require_uppercase)
            elif rule.rule_type == 'require_lowercase':
                require_lowercase = rule.parameters.get('required', require_lowercase)
            elif rule.rule_type == 'require_digits':
                require_digits = rule.parameters.get('required', require_digits)
            elif rule.rule_type == 'require_special':
                require_special = rule.parameters.get('required', require_special)

        # Check requirements
        if len(value) < min_length:
            errors.append(f"Password too short (minimum {min_length} characters)")

        if require_uppercase and not re.search(r'[A-Z]', value):
            errors.append("Password must contain at least one uppercase letter")

        if require_lowercase and not re.search(r'[a-z]', value):
            errors.append("Password must contain at least one lowercase letter")

        if require_digits and not re.search(r'\d', value):
            errors.append("Password must contain at least one digit")

        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append("Password must contain at least one special character")

        # Check for common weak patterns
        if value.lower() in ['password', '123456', 'qwerty', 'admin']:
            errors.append("Password is too common")

        # Check for sequential characters
        if re.search(r'(012|123|234|345|456|567|678|789|890)', value):
            warnings.append("Password contains sequential digits")

        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', value.lower()):
            warnings.append("Password contains sequential letters")

        return ValidationResult(
            is_valid=len(errors) == 0,
            value=value,
            errors=errors,
            warnings=warnings
        )

    async def _validate_url(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate URL input"""
        errors = []

        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["URL must be a string"]
            )

        try:
            parsed = urlparse(value)

            # Check scheme
            allowed_schemes = ['http', 'https']
            if parsed.scheme not in allowed_schemes:
                errors.append(f"URL scheme must be one of: {', '.join(allowed_schemes)}")

            # Check netloc (domain)
            if not parsed.netloc:
                errors.append("URL must include a valid domain")

            # Check for suspicious patterns
            if '..' in value or '//' in parsed.path:
                errors.append("URL contains suspicious path patterns")

            # Check domain length
            if len(parsed.netloc) > 253:
                errors.append("Domain name too long")

            return ValidationResult(
                is_valid=len(errors) == 0,
                value=value,
                errors=errors
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=[f"Invalid URL format: {str(e)}"]
            )

    async def _validate_numeric(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate numeric input"""
        errors = []

        # Try to convert to number
        try:
            if isinstance(value, str):
                # Handle different number formats
                if '.' in value:
                    num_value = float(value)
                else:
                    num_value = int(value)
            else:
                num_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["Value must be a valid number"]
            )

        # Apply rules
        for rule in rules:
            if rule.rule_type == 'range':
                min_val = rule.parameters.get('min', float('-inf'))
                max_val = rule.parameters.get('max', float('inf'))

                if num_value < min_val:
                    errors.append(f"Value too small (minimum {min_val})")
                elif num_value > max_val:
                    errors.append(f"Value too large (maximum {max_val})")

            elif rule.rule_type == 'integer_only':
                if not isinstance(num_value, int):
                    errors.append("Value must be an integer")

            elif rule.rule_type == 'positive_only':
                if num_value <= 0:
                    errors.append("Value must be positive")

        return ValidationResult(
            is_valid=len(errors) == 0,
            value=value,
            sanitized_value=num_value,
            errors=errors
        )

    async def _validate_date(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate date input"""
        from datetime import datetime, date

        errors = []

        if isinstance(value, str):
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S'
            ]

            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue

            if parsed_date is None:
                return ValidationResult(
                    is_valid=False,
                    value=value,
                    errors=["Invalid date format"]
                )
        elif isinstance(value, (datetime, date)):
            parsed_date = value if isinstance(value, datetime) else datetime.combine(value, datetime.min.time())
        else:
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["Value must be a date or date string"]
            )

        # Apply rules
        for rule in rules:
            if rule.rule_type == 'future_only':
                if parsed_date < datetime.now():
                    errors.append("Date must be in the future")

            elif rule.rule_type == 'past_only':
                if parsed_date > datetime.now():
                    errors.append("Date must be in the past")

            elif rule.rule_type == 'age_limit':
                min_age = rule.parameters.get('min_age', 0)
                max_age = rule.parameters.get('max_age', 150)

                age = (datetime.now() - parsed_date).days / 365.25
                if age < min_age:
                    errors.append(f"Age too young (minimum {min_age} years)")
                elif age > max_age:
                    errors.append(f"Age too old (maximum {max_age} years)")

        return ValidationResult(
            is_valid=len(errors) == 0,
            value=value,
            sanitized_value=parsed_date,
            errors=errors
        )

    async def _validate_json(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate JSON input"""
        import json

        errors = []

        if isinstance(value, str):
            try:
                parsed_json = json.loads(value)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    is_valid=False,
                    value=value,
                    errors=[f"Invalid JSON format: {str(e)}"]
                )
        elif isinstance(value, (dict, list)):
            parsed_json = value
        else:
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["Value must be valid JSON or dict/list"]
            )

        # Apply rules
        for rule in rules:
            if rule.rule_type == 'max_depth':
                max_depth = rule.parameters.get('depth', 10)
                depth = self._calculate_json_depth(parsed_json)
                if depth > max_depth:
                    errors.append(f"JSON too deeply nested (maximum depth {max_depth})")

            elif rule.rule_type == 'max_size':
                max_size = rule.parameters.get('size', 1000000)  # 1MB default
                size = len(json.dumps(parsed_json))
                if size > max_size:
                    errors.append(f"JSON too large (maximum {max_size} bytes)")

            elif rule.rule_type == 'required_fields':
                required = rule.parameters.get('fields', [])
                if isinstance(parsed_json, dict):
                    missing = [field for field in required if field not in parsed_json]
                    if missing:
                        errors.append(f"Missing required fields: {', '.join(missing)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            value=value,
            sanitized_value=parsed_json,
            errors=errors
        )

    async def _validate_file(self, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate file input"""
        errors = []

        # This is a basic implementation - in production you'd check file metadata
        if hasattr(value, 'filename'):
            filename = value.filename
        elif isinstance(value, str):
            filename = value
        else:
            return ValidationResult(
                is_valid=False,
                value=value,
                errors=["Invalid file input"]
            )

        # Apply rules
        for rule in rules:
            if rule.rule_type == 'allowed_extensions':
                allowed = rule.parameters.get('extensions', [])
                if allowed:
                    ext = filename.split('.')[-1].lower() if '.' in filename else ''
                    if ext not in [e.lower() for e in allowed]:
                        errors.append(f"File extension not allowed: {ext}")

            elif rule.rule_type == 'max_size':
                max_size = rule.parameters.get('size', 10 * 1024 * 1024)  # 10MB default
                if hasattr(value, 'size') and value.size > max_size:
                    errors.append(f"File too large (maximum {max_size} bytes)")

            elif rule.rule_type == 'filename_pattern':
                pattern = rule.parameters.get('pattern')
                if pattern and not re.match(pattern, filename):
                    errors.append("Filename does not match required pattern")

        return ValidationResult(
            is_valid=len(errors) == 0,
            value=value,
            errors=errors
        )

    # Sanitization methods
    async def _sanitize_sql_injection(self, value: str) -> tuple:
        """Sanitize SQL injection attempts"""
        changes = []
        flags = []

        if not isinstance(value, str):
            return value, changes, flags

        # Remove or escape dangerous SQL keywords
        dangerous_patterns = [
            (r';\s*drop\s+table', '; DROP TABLE'),
            (r';\s*delete\s+from', '; DELETE FROM'),
            (r';\s*update\s+.*set', '; UPDATE ... SET'),
            (r'union\s+select', 'UNION SELECT'),
            (r'--', '--'),
            (r'/\*.*?\*/', '/*...*/')
        ]

        sanitized = value
        for pattern, description in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                flags.append(f"Potential SQL injection: {description}")
                # Remove the dangerous pattern
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
                changes.append(f"Removed potential SQL injection: {description}")

        return sanitized, changes, flags

    async def _sanitize_xss(self, value: str) -> tuple:
        """Sanitize XSS attempts"""
        changes = []
        flags = []

        if not isinstance(value, str):
            return value, changes, flags

        # Remove dangerous HTML/JS patterns
        dangerous_patterns = [
            (r'<script[^>]*>.*?</script>', '<script>'),
            (r'javascript:', 'javascript:'),
            (r'on\w+\s*=', 'on*='),
            (r'<iframe[^>]*>.*?</iframe>', '<iframe>'),
            (r'<object[^>]*>.*?</object>', '<object>')
        ]

        sanitized = value
        for pattern, description in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                flags.append(f"Potential XSS: {description}")
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
                changes.append(f"Removed potential XSS: {description}")

        return sanitized, changes, flags

    async def _sanitize_command_injection(self, value: str) -> tuple:
        """Sanitize command injection attempts"""
        changes = []
        flags = []

        if not isinstance(value, str):
            return value, changes, flags

        # Remove command injection patterns
        dangerous_patterns = [
            (r';\s*(?:ls|cat|rm|cp|mv|chmod|chown)', '; command'),
            (r'\|\s*(?:ls|cat|rm|cp|mv)', '| command'),
            (r'`.*?`', '`command`'),
            (r'\$\(.*?\)', '$(command)')
        ]

        sanitized = value
        for pattern, description in dangerous_patterns:
            if re.search(pattern, sanitized):
                flags.append(f"Potential command injection: {description}")
                sanitized = re.sub(pattern, '', sanitized)
                changes.append(f"Removed potential command injection: {description}")

        return sanitized, changes, flags

    async def _sanitize_path_traversal(self, value: str) -> tuple:
        """Sanitize path traversal attempts"""
        changes = []
        flags = []

        if not isinstance(value, str):
            return value, changes, flags

        # Remove path traversal patterns
        dangerous_patterns = [
            (r'\.\./', '../'),
            (r'\.\.\\', '..\\'),
            (r'%2e%2e%2f', '%2e%2e%2f'),
            (r'%2e%2e%5c', '%2e%2e%5c')
        ]

        sanitized = value
        for pattern, description in dangerous_patterns:
            if re.search(pattern, sanitized):
                flags.append(f"Potential path traversal: {description}")
                sanitized = re.sub(pattern, '', sanitized)
                changes.append(f"Removed potential path traversal: {description}")

        return sanitized, changes, flags

    async def _encode_html_entities(self, value: str) -> tuple:
        """Encode HTML entities"""
        import html

        if not isinstance(value, str):
            return value, [], []

        original = value
        sanitized = html.escape(value)

        changes = []
        if sanitized != original:
            changes.append("Encoded HTML entities")

        return sanitized, changes, []

    async def _normalize_unicode(self, value: str) -> tuple:
        """Normalize unicode characters"""
        if not isinstance(value, str):
            return value, [], []

        original = value
        sanitized = unicodedata.normalize('NFKC', value)

        changes = []
        if sanitized != original:
            changes.append("Normalized unicode characters")

        return sanitized, changes, []

    def _calculate_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate JSON object depth"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_json_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_json_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth

    def add_custom_validator(self, name: str, validator_func: Callable):
        """Add custom validator"""
        self.custom_validators[name] = validator_func

    def add_custom_sanitizer(self, name: str, sanitizer_func: Callable):
        """Add custom sanitizer"""
        self.sanitizers[name] = sanitizer_func


# Global validator instance
enterprise_validator = EnterpriseValidator()


# FastAPI integration
async def validate_request_data(input_type: str, value: Any,
                              rules: Optional[List[ValidationRule]] = None,
                              sanitizers: Optional[List[str]] = None):
    """Validate request data with enterprise validation"""
    return await enterprise_validator.validate_and_sanitize(
        input_type, value, rules, sanitizers
    )


# Pydantic integration
class ValidatedString(str):
    """String with built-in validation"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    async def validate(cls, value):
        result = await enterprise_validator.validate_input('string', value)
        if not result.is_valid:
            raise ValueError(f"Validation failed: {', '.join(result.errors)}")
        return cls(result.sanitized_value or result.value)


class ValidatedEmail(str):
    """Email with built-in validation"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    async def validate(cls, value):
        result = await enterprise_validator.validate_input('email', value)
        if not result.is_valid:
            raise ValueError(f"Email validation failed: {', '.join(result.errors)}")
        return cls(result.sanitized_value or result.value)


class ValidatedPassword(str):
    """Password with built-in validation"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    async def validate(cls, value):
        result = await enterprise_validator.validate_input('password', value)
        if not result.is_valid:
            raise ValueError(f"Password validation failed: {', '.join(result.errors)}")
        return cls(result.value)  # Don't sanitize passwords


class ValidatedURL(str):
    """URL with built-in validation"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    async def validate(cls, value):
        result = await enterprise_validator.validate_input('url', value)
        if not result.is_valid:
            raise ValueError(f"URL validation failed: {', '.join(result.errors)}")
        return cls(result.value)