from __future__ import annotations

from .base import *  # noqa: F403
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

# Validate SECRET_KEY is properly set in production
_INSECURE_KEYS = ("changeme", "dev-only-insecure-key-do-not-use-in-production", "dev-secret-key-12345", "")
if SECRET_KEY in _INSECURE_KEYS:  # noqa: F405
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be set to a unique, unpredictable value in production. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(50))\""
    )

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_REFERRER_POLICY = "same-origin"

