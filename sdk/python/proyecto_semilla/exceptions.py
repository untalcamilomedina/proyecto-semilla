"""
Proyecto Semilla SDK Exceptions - Custom error handling
"""


class ProyectoSemillaError(Exception):
    """Base exception for Proyecto Semilla SDK"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ProyectoSemillaError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(message, 401, details)


class AuthorizationError(ProyectoSemillaError):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Insufficient permissions", details: dict = None):
        super().__init__(message, 403, details)


class APIError(ProyectoSemillaError):
    """Raised when API calls fail"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message, status_code, details)


class ValidationError(ProyectoSemillaError):
    """Raised when data validation fails"""
    def __init__(self, message: str, field: str = None, details: dict = None):
        details = details or {}
        if field:
            details['field'] = field
        super().__init__(message, 400, details)


class NetworkError(ProyectoSemillaError):
    """Raised when network connectivity fails"""
    def __init__(self, message: str = "Network connection failed", details: dict = None):
        super().__init__(message, 0, details)


class TimeoutError(ProyectoSemillaError):
    """Raised when requests timeout"""
    def __init__(self, message: str = "Request timeout", details: dict = None):
        super().__init__(message, 408, details)


class ModuleGenerationError(ProyectoSemillaError):
    """Raised when module generation fails"""
    def __init__(self, message: str, module_name: str = None, details: dict = None):
        details = details or {}
        if module_name:
            details['module_name'] = module_name
        super().__init__(message, 500, details)


class ConfigurationError(ProyectoSemillaError):
    """Raised when SDK configuration is invalid"""
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        details = details or {}
        if config_key:
            details['config_key'] = config_key
        super().__init__(message, 500, details)


class TenantNotFoundError(ProyectoSemillaError):
    """Raised when requested tenant is not found"""
    def __init__(self, tenant_id: str, details: dict = None):
        details = details or {}
        details['tenant_id'] = tenant_id
        super().__init__(f"Tenant '{tenant_id}' not found", 404, details)


class UserNotFoundError(ProyectoSemillaError):
    """Raised when requested user is not found"""
    def __init__(self, user_id: str, details: dict = None):
        details = details or {}
        details['user_id'] = user_id
        super().__init__(f"User '{user_id}' not found", 404, details)


class ModuleNotFoundError(ProyectoSemillaError):
    """Raised when requested module is not found"""
    def __init__(self, module_name: str, details: dict = None):
        details = details or {}
        details['module_name'] = module_name
        super().__init__(f"Module '{module_name}' not found", 404, details)


class RateLimitError(ProyectoSemillaError):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, details: dict = None):
        details = details or {}
        if retry_after:
            details['retry_after'] = retry_after
        super().__init__(message, 429, details)


class ServerError(ProyectoSemillaError):
    """Raised when server returns 5xx errors"""
    def __init__(self, message: str = "Internal server error", status_code: int = 500, details: dict = None):
        super().__init__(message, status_code, details)


# Error handling utilities
def handle_api_error(response) -> None:
    """Handle API response errors and raise appropriate exceptions"""
    if response.status_code == 401:
        raise AuthenticationError("Invalid or expired token")
    elif response.status_code == 403:
        raise AuthorizationError("Access denied")
    elif response.status_code == 404:
        raise APIError("Resource not found", 404)
    elif response.status_code == 422:
        raise ValidationError("Invalid request data")
    elif response.status_code == 429:
        retry_after = response.headers.get('Retry-After')
        raise RateLimitError(retry_after=int(retry_after) if retry_after else None)
    elif response.status_code >= 500:
        raise ServerError(f"Server error: {response.status_code}")
    elif not response.ok:
        raise APIError(f"API error: {response.status_code}")


def handle_request_error(error) -> None:
    """Handle request-level errors"""
    if isinstance(error, TimeoutError):
        raise TimeoutError("Request timed out")
    elif isinstance(error, ConnectionError):
        raise NetworkError("Connection failed")
    else:
        raise APIError(f"Request failed: {str(error)}")