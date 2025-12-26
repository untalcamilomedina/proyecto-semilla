from __future__ import annotations

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = env.list(  # type: ignore[name-defined]  # noqa: F405
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "web", "frontend", ".acme.dev"],
)


# Needed when running behind a reverse proxy (e.g. Next.js rewrites in Docker).
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=True)  # type: ignore[name-defined]  # noqa: F405

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
)

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
)



# Disable manifest storage in dev/test to avoid running collectstatic
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
