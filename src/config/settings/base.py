from __future__ import annotations

import os
from pathlib import Path

import dj_database_url
from environs import Env

from .plugins import ENABLE_CMS, MULTITENANT_MODE, optional_apps

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"

env = Env()
env.read_env(os.environ.get("ENV_FILE"))  # optional explicit path

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="changeme")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
DOMAIN_BASE = env.str("DOMAIN_BASE", default="notionapps.dev")
FRONTEND_URL = env.str("FRONTEND_URL", default="http://localhost:3000")

WAGTAIL_APPS: list[str] = []
if ENABLE_CMS:
    WAGTAIL_APPS = [
        "wagtail.contrib.forms",
        "wagtail.contrib.redirects",
        "wagtail.embeds",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.images",
        "wagtail.search",
        "wagtail.admin",
        "wagtail",
        "modelcluster",
        "taggit",
    ]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.notion",
    "guardian",
    "rules.apps.AutodiscoverRulesConfig",
    "waffle",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "axes",
    "csp",
    "djstripe",
    "anymail",
    "silk",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    # Wagtail (optional)
] + WAGTAIL_APPS + [
    # First-party
    "common",
    "core",
    "api",
    "billing",
    "multitenant",
    "oauth",
    "integrations",
] + optional_apps()

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
]
if MULTITENANT_MODE == "schema":
    MIDDLEWARE.append("multitenant.middleware.TenantMiddleware")
MIDDLEWARE += [
    "common.middleware.MetricsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "silk.middleware.SilkyMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
AXES_ENABLED = env.bool("ENABLE_AXES", default=not DEBUG)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "common.context_processors.tenant_branding",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        env.str("DATABASE_URL", default="postgresql://postgres:postgres@localhost:5432/notionapps"),
        conn_max_age=600,
    )
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
]

SITE_ID = 1



# Email Configuration
EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env.str("EMAIL_HOST", default="mailpit")
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="noreply@notionapps.dev")
SERVER_EMAIL = env.str("SERVER_EMAIL", default="server@notionapps.dev")

ANYMAIL = {
    "SENDGRID_API_KEY": env.str("ANYMAIL_API_KEY", default=""),
    "WEBHOOK_SECRET": env.str("ANYMAIL_WEBHOOK_SECRET", default=""),
}

# Silk Profiling
SILKY_PYTHON_PROFILER = True
SILKY_AUTHENTICATION = True  # User must be logged in
SILKY_AUTHORISATION = True  # User must be staff

ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = env.str("SESSION_COOKIE_SAMESITE", default="Lax")
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
CSRF_COOKIE_HTTPONLY = env.bool("CSRF_COOKIE_HTTPONLY", default=True)
CSRF_COOKIE_SAMESITE = env.str("CSRF_COOKIE_SAMESITE", default="Lax")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = ROOT_DIR / "staticfiles"
STATICFILES_DIRS = [SRC_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Social Account Providers
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "notion": {  # Using generic OpenID/OAuth2 provider if specific notion provider is not available in allauth yet, or custom adapter
        "SCOPE": ["public"],
        "VERIFIED_EMAIL": True,
    }
}
SOCIALACCOUNT_ADAPTER = "oauth.adapters.CustomSocialAccountAdapter"

MEDIA_URL = "/media/"
MEDIA_ROOT = ROOT_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "common.api.exceptions.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.authentication.ApiKeyAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": env.str("API_USER_RATE", default="1000/day"),
        "anon": env.str("API_ANON_RATE", default="100/day"),
    },
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_VERSION": "v1",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "NotionApps API",
    "DESCRIPTION": "Versioned DRF API for NotionApps.",
    "VERSION": "v1",
    "SERVE_INCLUDE_SCHEMA": False,
}

CELERY_BROKER_URL = env.str("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env.str("S3_ACCESS_KEY", default=""),
            "secret_key": env.str("S3_SECRET_KEY", default=""),
            "bucket_name": env.str("S3_BUCKET_NAME", default=""),
            "endpoint_url": env.str("S3_ENDPOINT_URL", default=""),
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SENTRY_DSN = env.str("SENTRY_DSN", default="")

STRIPE_SECRET_KEY = env.str("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env.str("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_DEFAULT_CURRENCY = env.str("STRIPE_DEFAULT_CURRENCY", default="usd")
STRIPE_LIVE_MODE = env.bool("STRIPE_LIVE_MODE", default=False)
DJSTRIPE_WEBHOOK_SECRET = env.str("DJSTRIPE_WEBHOOK_SECRET", default=STRIPE_WEBHOOK_SECRET)
DJSTRIPE_USE_NATIVE_JSONFIELD = True
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"

AXES_FAILURE_LIMIT = env.int("AXES_FAILURE_LIMIT", default=5)
AXES_COOLOFF_TIME = env.int("AXES_COOLOFF_TIME", default=1)  # hours
AXES_LOCK_OUT_AT_FAILURE = True
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_CACHE = "default"

CONTENT_SECURITY_POLICY_REPORT_ONLY_ENABLED = env.bool("CSP_REPORT_ONLY", default=DEBUG)

CONTENT_SECURITY_POLICY_DIRECTIVES = {
    "default-src": ("'self'",),
    "script-src": (
        "'self'",
        "'unsafe-inline'",
        "https://cdn.tailwindcss.com",
        "https://unpkg.com",
        "https://js.stripe.com",
        "https://cdn.jsdelivr.net",
    ),
    "style-src": ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"),
    "font-src": ("'self'", "https://fonts.gstatic.com"),
    "img-src": ("'self'", "data:", "https://cdn.jsdelivr.net"),
    "connect-src": (
        "'self'",
        "https://sentry.io",
        "https://*.ingest.sentry.io",
    ),
    "frame-src": ("'self'", "https://js.stripe.com"),
}

if CONTENT_SECURITY_POLICY_REPORT_ONLY_ENABLED:
    CONTENT_SECURITY_POLICY_REPORT_ONLY = {"DIRECTIVES": CONTENT_SECURITY_POLICY_DIRECTIVES}
else:
    CONTENT_SECURITY_POLICY = {"DIRECTIVES": CONTENT_SECURITY_POLICY_DIRECTIVES}

# Additional security headers (prod overrides allowed via env)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = env.str("X_FRAME_OPTIONS", default="DENY")
SECURE_REFERRER_POLICY = env.str("SECURE_REFERRER_POLICY", default="same-origin")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": env.str("LOG_FORMAT", default="json"),
        }
    },
    "root": {"handlers": ["console"], "level": env.str("LOG_LEVEL", default="INFO")},
}

# Sentry (optional)
SENTRY_ENVIRONMENT = env.str(
    "SENTRY_ENVIRONMENT", default="dev" if DEBUG else "prod"
)
SENTRY_RELEASE = env.str("SENTRY_RELEASE", default="")
SENTRY_TRACES_SAMPLE_RATE = env.float(
    "SENTRY_TRACES_SAMPLE_RATE", default=0.0 if DEBUG else 0.1
)

if SENTRY_DSN:
    try:  # pragma: no cover
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=SENTRY_ENVIRONMENT,
            release=SENTRY_RELEASE or None,
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
            send_default_pii=False,
            integrations=[DjangoIntegration(), CeleryIntegration()],
        )
    except Exception:
        pass

MULTITENANT_MODE = MULTITENANT_MODE
