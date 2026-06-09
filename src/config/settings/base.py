from __future__ import annotations

import os
from pathlib import Path

import dj_database_url
from environs import Env

from .plugins import MULTITENANT_MODE, optional_apps

ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"

env = Env()
env.read_env(os.environ.get("ENV_FILE"))  # optional explicit path

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="dev-only-insecure-key-do-not-use-in-production")
DEBUG = env.bool("DEBUG", default=False)

# Clave dedicada para cifrado de campos (common.encryption). Si no se define,
# se deriva de SECRET_KEY (no recomendado en producción: impide rotar SECRET_KEY).
FIELD_ENCRYPTION_KEY = env.str("FIELD_ENCRYPTION_KEY", default="")

# Token Bearer para proteger /metrics fuera de DEBUG (vacío = endpoint cerrado).
METRICS_TOKEN = env.str("METRICS_TOKEN", default="")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
DOMAIN_BASE = env.str("DOMAIN_BASE", default="localhost")
FRONTEND_URL = env.str("FRONTEND_URL", default="http://localhost:3000")

# Wagtail removed — CMS now uses MDX via Next.js frontend

INSTALLED_APPS = [
    # Modeltranslation (must be before admin and all translated apps)
    "modeltranslation",
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
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "auditlog",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # First-party
    "common",
    "core",
    "api",
    "billing",
    "multitenant",
    "oauth",
    *optional_apps(),
]

# Silk (profiler) se añade en dev.py — debe estar instalado si y solo si
# DEBUG final es True (urls.py monta silk.urls según settings.DEBUG).

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]
if MULTITENANT_MODE == "schema":
    MIDDLEWARE.append("multitenant.middleware.TenantMiddleware")
MIDDLEWARE += [
    "corsheaders.middleware.CorsMiddleware",
    "common.middleware.MetricsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
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
        env.str(
            "DATABASE_URL", default="postgresql://postgres:postgres@localhost:5432/proyecto_semilla"
        ),
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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

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
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="noreply@localhost")
SERVER_EMAIL = env.str("SERVER_EMAIL", default="server@localhost")

ANYMAIL = {
    "SENDGRID_API_KEY": env.str("ANYMAIL_API_KEY", default=""),
    "WEBHOOK_SECRET": env.str("ANYMAIL_WEBHOOK_SECRET", default=""),
}

# Silk Profiling
SILKY_PYTHON_PROFILER = True
SILKY_AUTHENTICATION = True  # User must be logged in
SILKY_AUTHORISATION = True  # User must be staff

# "optional" en dev; producción la fuerza a "mandatory" (ver prod.py, env-overridable)
ACCOUNT_EMAIL_VERIFICATION = env.str("ACCOUNT_EMAIL_VERIFICATION", default="optional")
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = env.str("SESSION_COOKIE_SAMESITE", default="Lax")
# cached_db: lectura rápida vía Redis con persistencia en Postgres.
# Un Redis caído no debe invalidar todas las sesiones (IGNORE_EXCEPTIONS=True arriba).
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
CSRF_COOKIE_HTTPONLY = env.bool("CSRF_COOKIE_HTTPONLY", default=True)
CSRF_COOKIE_SAMESITE = env.str("CSRF_COOKIE_SAMESITE", default="Lax")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# i18n — Supported languages for model translation (django-modeltranslation)
LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
    ("pt", "Português"),
]

# Modeltranslation settings
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_FALLBACK_LANGUAGES = ("en",)

STATIC_URL = "/static/"
STATIC_ROOT = ROOT_DIR / "staticfiles"
STATICFILES_DIRS = [SRC_DIR / "static"]
# El storage de staticfiles se configura vía STORAGES (Django 5+); el antiguo
# STATICFILES_STORAGE fue eliminado en Django 5.1.

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
}
SOCIALACCOUNT_ADAPTER = "oauth.adapters.CustomSocialAccountAdapter"

MEDIA_URL = "/media/"
MEDIA_ROOT = ROOT_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "common.api.exceptions.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # JWT con binding al schema emisor (ver api.authentication)
        "api.authentication.TenantJWTAuthentication",
        "api.authentication.ApiKeyAuthentication",
        "rest_framework.authentication.SessionAuthentication",
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

PROJECT_NAME = env.str("PROJECT_NAME", default="Proyecto Semilla")

SPECTACULAR_SETTINGS = {
    "TITLE": f"{PROJECT_NAME} API",
    "DESCRIPTION": f"Versioned DRF API for {PROJECT_NAME}.",
    "VERSION": "v1",
    "SERVE_INCLUDE_SCHEMA": False,
}

# JWT Authentication (stateless)
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    # Clave dedicada para JWT: permite rotar SECRET_KEY sin invalidar tokens
    # y evita que un default inseguro de SECRET_KEY firme tokens en prod.
    "SIGNING_KEY": env.str("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "api.serializers_auth.TenantTokenObtainPairSerializer",
}

# Broker de Celery separable del cache (por defecto comparte la URL de Redis).
CELERY_BROKER_URL = env.str(
    "CELERY_BROKER_URL", default=env.str("REDIS_URL", default="redis://localhost:6379/0")
)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default=CELERY_BROKER_URL)

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

# Subidas de archivos del CMS (allowlist de extensiones + tamaño máximo)
CMS_ALLOWED_UPLOAD_EXTENSIONS = env.list(
    "CMS_ALLOWED_UPLOAD_EXTENSIONS",
    default=["jpg", "jpeg", "png", "gif", "webp", "svg", "pdf", "mp4", "webm", "mp3"],
)
CMS_MAX_UPLOAD_SIZE_MB = env.int("CMS_MAX_UPLOAD_SIZE_MB", default=20)

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
AXES_RESET_ON_SUCCESS = True
AXES_CACHE = "default"

CONTENT_SECURITY_POLICY_REPORT_ONLY_ENABLED = env.bool("CSP_REPORT_ONLY", default=DEBUG)

# NOTA: 'unsafe-inline' y los CDNs existen porque los templates Django
# (allauth/base.html) aún cargan Tailwind/HTMX desde CDN. Endurecer esta CSP
# requiere migrar esos templates a assets compilados (ver docs/auditoria).
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
    "style-src": (
        "'self'",
        "'unsafe-inline'",
        "https://fonts.googleapis.com",
        "https://cdn.jsdelivr.net",
    ),
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
SENTRY_ENVIRONMENT = env.str("SENTRY_ENVIRONMENT", default="dev" if DEBUG else "prod")
SENTRY_RELEASE = env.str("SENTRY_RELEASE", default="")
SENTRY_TRACES_SAMPLE_RATE = env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0 if DEBUG else 0.1)

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
    except Exception:  # noqa: S110 — Sentry es opcional; no debe impedir el arranque
        pass
