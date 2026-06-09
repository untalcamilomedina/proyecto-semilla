from __future__ import annotations

import warnings

from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

# Validate SECRET_KEY is properly set in production
_INSECURE_KEYS = (
    "changeme",
    "dev-only-insecure-key-do-not-use-in-production",
    "dev-secret-key-12345",
    "",
)
if SECRET_KEY in _INSECURE_KEYS:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be set to a unique, unpredictable value in production. "
        'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(50))"'
    )

if not FIELD_ENCRYPTION_KEY:
    warnings.warn(
        "FIELD_ENCRYPTION_KEY no está definida: el cifrado de campos se deriva de "
        "SECRET_KEY y rotarla dejará ilegibles los datos cifrados. Define una clave dedicada.",
        stacklevel=1,
    )

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_REFERRER_POLICY = "same-origin"

# CORS explícito para el frontend en producción (lista separada por comas).
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# Verificación de email obligatoria en producción (override por env si hace falta).
ACCOUNT_EMAIL_VERIFICATION = env.str("ACCOUNT_EMAIL_VERIFICATION", default="mandatory")
