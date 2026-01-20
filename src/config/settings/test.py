from .dev import *

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
