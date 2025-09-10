"""
Secure cookie management for Proyecto Semilla
Handles JWT tokens in HTTP-only cookies for enhanced security
"""

import os
from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi import Response, Request
from fastapi.responses import JSONResponse

from app.core.config import settings


class SecureCookieManager:
    """
    Manages secure HTTP-only cookies for JWT tokens
    """

    def __init__(self):
        self.access_token_cookie_name = "access_token"
        self.refresh_token_cookie_name = "refresh_token"
        self.tenant_cookie_name = "current_tenant"

        # Cookie security settings
        self.secure = os.getenv("COOKIE_SECURE", "false").lower() == "true"
        self.http_only = True
        self.same_site = "lax"  # Can be "strict", "lax", or "none"
        self.domain = os.getenv("COOKIE_DOMAIN", None)
        self.path = "/"

    def set_access_token_cookie(self, response: Response, token: str, expires_in: int = None):
        """Set access token in secure cookie"""
        if expires_in is None:
            expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds

        expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        response.set_cookie(
            key=self.access_token_cookie_name,
            value=token,
            expires=expires,
            httponly=self.http_only,
            secure=self.secure,
            samesite=self.same_site,
            domain=self.domain,
            path=self.path
        )

    def set_refresh_token_cookie(self, response: Response, token: str):
        """Set refresh token in secure cookie"""
        # Refresh tokens expire in 30 days
        expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        response.set_cookie(
            key=self.refresh_token_cookie_name,
            value=token,
            expires=expires,
            httponly=self.http_only,
            secure=self.secure,
            samesite=self.same_site,
            domain=self.domain,
            path=self.path
        )

    def set_tenant_cookie(self, response: Response, tenant_id: str, tenant_name: str):
        """Set current tenant information in cookie"""
        # Tenant cookie expires in 30 days
        expires = datetime.now(timezone.utc) + timedelta(days=30)

        response.set_cookie(
            key=self.tenant_cookie_name,
            value=f"{tenant_id}:{tenant_name}",
            expires=expires,
            httponly=False,  # Allow JavaScript access for UI
            secure=self.secure,
            samesite=self.same_site,
            domain=self.domain,
            path=self.path
        )

    def get_access_token_from_cookie(self, request: Request) -> Optional[str]:
        """Extract access token from cookie"""
        return request.cookies.get(self.access_token_cookie_name)

    def get_refresh_token_from_cookie(self, request: Request) -> Optional[str]:
        """Extract refresh token from cookie"""
        return request.cookies.get(self.refresh_token_cookie_name)

    def get_tenant_from_cookie(self, request: Request) -> Optional[tuple[str, str]]:
        """Extract tenant info from cookie (tenant_id, tenant_name)"""
        tenant_cookie = request.cookies.get(self.tenant_cookie_name)
        if tenant_cookie:
            parts = tenant_cookie.split(":", 1)
            if len(parts) == 2:
                return (parts[0], parts[1])
        return None

    def clear_auth_cookies(self, response: Response):
        """Clear all authentication cookies"""
        response.delete_cookie(
            key=self.access_token_cookie_name,
            path=self.path,
            domain=self.domain
        )
        response.delete_cookie(
            key=self.refresh_token_cookie_name,
            path=self.path,
            domain=self.domain
        )
        response.delete_cookie(
            key=self.tenant_cookie_name,
            path=self.path,
            domain=self.domain
        )

    def create_login_response(self, access_token: str, refresh_token: str,
                            tenant_id: str, tenant_name: str) -> JSONResponse:
        """Create login response with secure cookies"""
        response = JSONResponse({
            "message": "Login successful",
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "tenant_id": tenant_id,
            "tenant_name": tenant_name
        })

        # Set secure cookies
        self.set_access_token_cookie(response, access_token)
        self.set_refresh_token_cookie(response, refresh_token)
        self.set_tenant_cookie(response, tenant_id, tenant_name)

        return response

    def create_logout_response(self) -> JSONResponse:
        """Create logout response that clears cookies"""
        response = JSONResponse({"message": "Successfully logged out"})
        self.clear_auth_cookies(response)
        return response


# Global cookie manager instance
cookie_manager = SecureCookieManager()


def get_cookie_manager() -> SecureCookieManager:
    """Dependency injection for cookie manager"""
    return cookie_manager