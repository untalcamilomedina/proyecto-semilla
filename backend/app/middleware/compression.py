"""
Advanced Response Compression Middleware for Proyecto Semilla
Implements Brotli and Gzip compression for optimal performance
"""

import gzip
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Try to import brotli, fallback to gzip only
try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False


class AdvancedCompressionMiddleware(BaseHTTPMiddleware):
    """
    Advanced compression middleware supporting Brotli and Gzip
    Automatically compresses responses based on client capabilities and content size
    """

    def __init__(self, app: Callable, minimum_size: int = 1000, brotli_quality: int = 6):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.brotli_quality = brotli_quality

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Compress response based on client capabilities
        Priority: Brotli > Gzip > No compression
        """
        response = await call_next(request)

        # Skip compression for small responses
        # Handle different response types (StreamingResponse doesn't have .body)
        try:
            response_size = len(response.body) if hasattr(response, 'body') else self.minimum_size + 1
            if response_size < self.minimum_size:
                return response
        except (AttributeError, TypeError):
            # For streaming responses or other types, skip compression
            return response

        # Skip compression for already compressed content
        content_type = response.headers.get("content-type", "")
        if any(compressed_type in content_type for compressed_type in [
            "image/", "video/", "audio/", "application/octet-stream"
        ]):
            return response

        # Get client accepted encodings
        accept_encoding = request.headers.get("accept-encoding", "").lower()

        # Try Brotli first (better compression) if available
        if BROTLI_AVAILABLE and "br" in accept_encoding:
            try:
                compressed_body = brotli.compress(
                    response.body,
                    quality=self.brotli_quality
                )

                # Only use if compression is effective (>10% reduction)
                if len(compressed_body) < len(response.body) * 0.9:
                    response.body = compressed_body
                    response.headers["content-encoding"] = "br"
                    response.headers["content-length"] = str(len(compressed_body))
                    response.headers["x-compression"] = "brotli"
                    return response

            except Exception as e:
                # Log error but continue with gzip
                print(f"Brotli compression failed: {e}")
        elif not BROTLI_AVAILABLE and "br" in accept_encoding:
            # Client supports Brotli but we don't have it installed
            print("Brotli requested but not available, falling back to gzip")

        # Try Gzip as fallback
        if "gzip" in accept_encoding:
            try:
                compressed_body = gzip.compress(response.body, compresslevel=6)

                # Only use if compression is effective
                if len(compressed_body) < len(response.body) * 0.95:
                    response.body = compressed_body
                    response.headers["content-encoding"] = "gzip"
                    response.headers["content-length"] = str(len(compressed_body))
                    response.headers["x-compression"] = "gzip"
                    return response

            except Exception as e:
                # Log error but continue without compression
                print(f"Gzip compression failed: {e}")

        # Return uncompressed response if compression fails
        response.headers["x-compression"] = "none"
        return response


class HTTP2ServerPushMiddleware(BaseHTTPMiddleware):
    """
    HTTP/2 Server Push middleware for critical resources
    Pushes related resources to improve loading performance
    """

    def __init__(self, app: Callable):
        super().__init__(app)
        self.push_resources = {
            "/api/v1/articles": [
                "</api/v1/categories>; rel=preload",
                "</api/v1/users/me>; rel=preload"
            ],
            "/api/v1/dashboard": [
                "</api/v1/articles/popular>; rel=preload",
                "</api/v1/analytics/overview>; rel=preload"
            ],
            "/": [
                "</api/v1/auth/me>; rel=preload",
                "</static/css/main.css>; rel=preload; as=style",
                "</static/js/app.js>; rel=preload; as=script"
            ]
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add Link headers for HTTP/2 server push
        """
        response = await call_next(request)

        # Add server push links for critical endpoints
        path = request.url.path
        if path in self.push_resources:
            links = self.push_resources[path]
            response.headers["Link"] = ", ".join(links)
            response.headers["x-server-push"] = "enabled"

        return response