"""
Security Headers Middleware for Proyecto Semilla
Implements comprehensive HTTP security headers
"""

from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add comprehensive security headers to all responses
    """

    def __init__(self, app, csp_policy: Optional[str] = None):
        super().__init__(app)
        self.csp_policy = csp_policy or self._get_default_csp()

    def _get_default_csp(self) -> str:
        """Get default Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response, request)

        return response

    def _add_security_headers(self, response: Response, request: Request):
        """Add all security headers to the response"""

        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy

        # HTTP Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options - Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection - XSS protection (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy - Restrict browser features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), "
            "accelerometer=(), gyroscope=(), speaker=(), "
            "fullscreen=(self), autoplay=()"
        )

        # Cross-Origin-Embedder-Policy - COEP
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cross-Origin-Opener-Policy - COOP
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin-Resource-Policy - CORP
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Origin-Agent-Cluster - Isolate origins
        response.headers["Origin-Agent-Cluster"] = "?1"

        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]

        # Remove X-Powered-By header
        if "x-powered-by" in response.headers:
            del response.headers["x-powered-by"]

        # Add custom security headers for API responses
        if isinstance(response, JSONResponse) or str(request.url.path).startswith("/api/"):
            # API-specific headers
            response.headers["X-API-Version"] = "v1"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"


# Utility functions for CSP customization
def create_csp_policy(
    default_src: str = "'self'",
    script_src: str = "'self' 'unsafe-inline'",
    style_src: str = "'self' 'unsafe-inline'",
    img_src: str = "'self' data: https:",
    connect_src: str = "'self'",
    frame_ancestors: str = "'none'",
    **kwargs
) -> str:
    """
    Create a custom Content Security Policy string

    Args:
        default_src: Default source policy
        script_src: Script source policy
        style_src: Style source policy
        img_src: Image source policy
        connect_src: Connect source policy
        frame_ancestors: Frame ancestors policy
        **kwargs: Additional CSP directives

    Returns:
        CSP policy string
    """
    directives = {
        "default-src": default_src,
        "script-src": script_src,
        "style-src": style_src,
        "img-src": img_src,
        "connect-src": connect_src,
        "frame-ancestors": frame_ancestors,
        **kwargs
    }

    return "; ".join(f"{key} {value}" for key, value in directives.items())


# Environment-based CSP configuration
def get_environment_csp() -> str:
    """Get CSP policy based on environment"""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return create_csp_policy(
            script_src="'self'",
            style_src="'self'",
            frame_ancestors="'none'"
        )
    elif env == "staging":
        return create_csp_policy(
            script_src="'self' 'unsafe-inline'",
            style_src="'self' 'unsafe-inline'",
            frame_ancestors="'none'"
        )
    else:  # development
        return create_csp_policy(
            script_src="'self' 'unsafe-inline' 'unsafe-eval'",
            style_src="'self' 'unsafe-inline'",
            frame_ancestors="'none'"
        )