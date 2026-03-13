import os

# Enable all optional modules for tests (must be set BEFORE importing settings)
os.environ.setdefault("ENABLE_LMS", "true")
os.environ.setdefault("ENABLE_COMMUNITY", "true")
os.environ.setdefault("ENABLE_MCP", "true")

from .dev import *  # noqa: F403, F401

# Allow all hosts during testing to support dynamic tenant domains
ALLOWED_HOSTS = ["*"]

# Ensure we don't rely on X-Forwarded-Host during tests unless explicitly needed
USE_X_FORWARDED_HOST = False

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use in-memory email backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# PostgreSQL ONLY — this project does not support SQLite.
# Tests must run inside Docker: docker compose exec web pytest tests/

# Disable Silk profiling in tests
SILKY_INTERCEPT_PERCENT = 0
