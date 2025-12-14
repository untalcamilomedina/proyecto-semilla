from __future__ import annotations

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = env.list(  # type: ignore[name-defined]  # noqa: F405
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "web", "frontend", ".acme.dev"],
)

# Needed when running behind a reverse proxy (e.g. Next.js rewrites in Docker).
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=True)  # type: ignore[name-defined]  # noqa: F405



# Disable manifest storage in dev/test to avoid running collectstatic
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
