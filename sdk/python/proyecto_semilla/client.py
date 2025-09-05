"""
Proyecto Semilla SDK Client - Main client for Vibecoding-native development
"""

import asyncio
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager
import httpx

from .auth import AuthManager
from .models import (
    Tenant, User, ModuleSpec, APIResponse, ModuleStatus,
    GenerationResult, TenantCreate, UserCreate, LoginRequest,
    ModuleGenerationRequest
)
from .exceptions import (
    AuthenticationError, APIError, ValidationError,
    NetworkError, TimeoutError, handle_api_error, handle_request_error
)


class ProyectoSemillaClient:
    """
    Main client for Proyecto Semilla SDK

    Provides a type-safe, async interface to Proyecto Semilla APIs
    with automatic authentication, error handling, and response parsing.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:7777",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        auto_refresh: bool = True
    ):
        """
        Initialize Proyecto Semilla client

        Args:
            base_url: Base URL of Proyecto Semilla instance
            api_key: API key for authentication (optional)
            timeout: Request timeout in seconds
            auto_refresh: Automatically refresh tokens when needed
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auto_refresh = auto_refresh

        # Initialize auth manager
        self.auth = AuthManager(api_key)

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self.auth.get_headers()
        )

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()

    async def _ensure_authenticated(self):
        """Ensure user is authenticated, refresh if needed"""
        if not self.auth.is_authenticated():
            raise AuthenticationError("Not authenticated. Please login first.")

        if self.auto_refresh and self.auth.needs_refresh():
            await self.auth.refresh_access_token(self.client)
            # Update client headers with new token
            self.client.headers.update(self.auth.get_headers())

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        if require_auth:
            await self._ensure_authenticated()

        try:
            if method.upper() == 'GET':
                response = await self.client.get(endpoint, params=params)
            elif method.upper() == 'POST':
                response = await self.client.post(endpoint, json=data)
            elif method.upper() == 'PUT':
                response = await self.client.put(endpoint, json=data)
            elif method.upper() == 'DELETE':
                response = await self.client.delete(endpoint)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Handle API errors
            handle_api_error(response)

            return response.json()

        except (httpx.TimeoutException, asyncio.TimeoutError):
            raise TimeoutError(f"Request to {endpoint} timed out")
        except httpx.ConnectError:
            raise NetworkError(f"Connection failed to {self.base_url}")
        except Exception as e:
            handle_request_error(e)
            raise

    # Authentication Methods
    async def login(self, email: str, password: str) -> User:
        """
        Authenticate user with email and password

        Args:
            email: User email
            password: User password

        Returns:
            User: Authenticated user information
        """
        login_data = LoginRequest(email=email, password=password)

        try:
            response = await self.client.post('/auth/login', json=login_data.dict())

            if response.status_code == 200:
                data = response.json()
                self.auth.set_tokens(
                    data['access_token'],
                    data['refresh_token'],
                    data['expires_in']
                )
                self.auth.set_user_info(data['user'])

                return User(**data['user'])
            else:
                raise AuthenticationError("Login failed")

        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")

    async def logout(self) -> bool:
        """Logout current user"""
        try:
            await self.client.post('/auth/logout')
            self.auth.clear_tokens()
            return True
        except Exception:
            # Even if logout fails, clear local tokens
            self.auth.clear_tokens()
            return True

    # Tenant Methods
    async def get_tenant(self, tenant_id: str) -> Tenant:
        """Get tenant by ID"""
        data = await self._make_request('GET', f'/tenants/{tenant_id}')
        return Tenant(**data)

    async def get_tenants(self) -> List[Tenant]:
        """Get all tenants (admin only)"""
        data = await self._make_request('GET', '/tenants/')
        return [Tenant(**tenant) for tenant in data]

    async def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """Create new tenant (admin only)"""
        data = await self._make_request('POST', '/tenants/', tenant_data.dict())
        return Tenant(**data)

    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Tenant:
        """Update tenant"""
        data = await self._make_request('PUT', f'/tenants/{tenant_id}', updates)
        return Tenant(**data)

    async def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant (admin only)"""
        await self._make_request('DELETE', f'/tenants/{tenant_id}')
        return True

    # User Methods
    async def get_user(self, user_id: str) -> User:
        """Get user by ID"""
        data = await self._make_request('GET', f'/users/{user_id}')
        return User(**data)

    async def get_users(self, tenant_id: Optional[str] = None) -> List[User]:
        """Get users (optionally filtered by tenant)"""
        params = {'tenant_id': tenant_id} if tenant_id else None
        data = await self._make_request('GET', '/users/', params=params)
        return [User(**user) for user in data]

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        data = await self._make_request('POST', '/users/', user_data.dict())
        return User(**data)

    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> User:
        """Update user"""
        data = await self._make_request('PUT', f'/users/{user_id}', updates)
        return User(**data)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        await self._make_request('DELETE', f'/users/{user_id}')
        return True

    # Module Methods
    async def generate_module(self, spec: ModuleSpec) -> GenerationResult:
        """
        Generate a complete module from specification

        This is the core Vibecoding functionality that allows LLMs
        to create complete applications automatically.
        """
        request = ModuleGenerationRequest(spec=spec)
        data = await self._make_request('POST', '/modules/generate', request.dict())
        return GenerationResult(**data)

    async def get_module_status(self, module_name: str) -> ModuleStatus:
        """Get status of a generated module"""
        data = await self._make_request('GET', f'/modules/{module_name}/status')
        return ModuleStatus(**data)

    async def list_modules(self) -> List[ModuleStatus]:
        """List all available modules"""
        data = await self._make_request('GET', '/modules/')
        return [ModuleStatus(**module) for module in data]

    async def deploy_module(self, module_name: str, tenant_id: str) -> bool:
        """Deploy module to specific tenant"""
        data = await self._make_request('POST', f'/modules/{module_name}/deploy',
                                      {'tenant_id': tenant_id})
        return data.get('success', False)

    async def update_module_docs(self, module_name: str) -> Dict[str, Any]:
        """Update auto-generated documentation for module"""
        data = await self._make_request('POST', f'/modules/{module_name}/update-docs')
        return data

    # Utility Methods
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = await self.client.get('/health', timeout=5.0)
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'version': response.json().get('version', 'unknown')
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.auth.is_authenticated()

    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user"""
        user_info = self.auth.get_user_info()
        return User(**user_info) if user_info else None

    def get_current_tenant(self) -> Optional[str]:
        """Get current tenant from token"""
        return self.auth.get_tenant_from_token()

    # Context manager for temporary API key usage
    @asynccontextmanager
    async def with_api_key(self, api_key: str):
        """Temporarily use a different API key"""
        original_key = self.auth.api_key
        self.auth.api_key = api_key
        self.client.headers.update(self.auth.get_headers())

        try:
            yield
        finally:
            self.auth.api_key = original_key
            self.client.headers.update(self.auth.get_headers())