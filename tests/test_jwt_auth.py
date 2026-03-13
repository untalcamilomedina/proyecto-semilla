"""Tests for JWT authentication and stateless auth flow."""

import pytest
from unittest.mock import patch, MagicMock


# ── JWT Serializer Tests ─────────────────────────────────────

class TestTenantTokenObtainPairSerializer:
    """Test custom JWT serializer with tenant claims."""

    def test_serializer_module_imports(self):
        """Verify serializer module can be imported."""
        from api.serializers_auth import TenantTokenObtainPairSerializer
        assert TenantTokenObtainPairSerializer is not None

    def test_serializer_inherits_from_base(self):
        """Verify custom serializer extends SimpleJWT base."""
        from api.serializers_auth import TenantTokenObtainPairSerializer
        from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
        assert issubclass(TenantTokenObtainPairSerializer, TokenObtainPairSerializer)

    def test_get_token_adds_email_claim(self):
        """Verify email is added as custom claim to token."""
        from api.serializers_auth import TenantTokenObtainPairSerializer

        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"

        # Create a dict-like mock token that behaves like RefreshToken
        mock_token = {}

        with patch(
            "rest_framework_simplejwt.serializers.TokenObtainPairSerializer.get_token",
            return_value=mock_token,
        ):
            with patch("core.models.Membership.objects") as mock_qs:
                mock_qs.filter.return_value.select_related.return_value.first.return_value = None
                token = TenantTokenObtainPairSerializer.get_token(mock_user)

        assert token["email"] == "test@example.com"
        assert token["first_name"] == "Test"
        assert token["last_name"] == "User"

    def test_get_token_includes_tenant_claims(self):
        """Verify tenant_id and role are added when membership exists."""
        from api.serializers_auth import TenantTokenObtainPairSerializer

        mock_user = MagicMock()
        mock_user.email = "admin@demo.com"
        mock_user.first_name = "Admin"
        mock_user.last_name = "Demo"

        mock_membership = MagicMock()
        mock_membership.organization_id = 42
        mock_membership.organization.slug = "demo-corp"
        mock_membership.role.slug = "owner"

        mock_token = {}

        with patch(
            "rest_framework_simplejwt.serializers.TokenObtainPairSerializer.get_token",
            return_value=mock_token,
        ):
            with patch("core.models.Membership.objects") as mock_qs:
                mock_qs.filter.return_value.select_related.return_value.first.return_value = mock_membership
                token = TenantTokenObtainPairSerializer.get_token(mock_user)

        assert token["tenant_id"] == 42
        assert token["tenant_slug"] == "demo-corp"
        assert token["role"] == "owner"

    def test_get_token_without_membership(self):
        """Verify token works even without active membership."""
        from api.serializers_auth import TenantTokenObtainPairSerializer

        mock_user = MagicMock()
        mock_user.email = "new@user.com"
        mock_user.first_name = ""
        mock_user.last_name = ""

        mock_token = {}

        with patch(
            "rest_framework_simplejwt.serializers.TokenObtainPairSerializer.get_token",
            return_value=mock_token,
        ):
            with patch("core.models.Membership.objects") as mock_qs:
                mock_qs.filter.return_value.select_related.return_value.first.return_value = None
                token = TenantTokenObtainPairSerializer.get_token(mock_user)

        assert token["email"] == "new@user.com"
        assert "tenant_id" not in token


# ── JWT Settings Tests ───────────────────────────────────────

class TestJWTSettings:
    """Test SIMPLE_JWT configuration is correct."""

    def test_jwt_settings_exist(self):
        """Verify SIMPLE_JWT is configured in Django settings."""
        from django.conf import settings
        assert hasattr(settings, "SIMPLE_JWT")

    def test_jwt_access_lifetime(self):
        """Verify access token lifetime is 15 minutes."""
        from django.conf import settings
        from datetime import timedelta
        assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == timedelta(minutes=15)

    def test_jwt_refresh_lifetime(self):
        """Verify refresh token lifetime is 7 days."""
        from django.conf import settings
        from datetime import timedelta
        assert settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] == timedelta(days=7)

    def test_jwt_rotation_enabled(self):
        """Verify refresh token rotation is enabled."""
        from django.conf import settings
        assert settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] is True

    def test_jwt_blacklist_enabled(self):
        """Verify blacklisting after rotation is enabled."""
        from django.conf import settings
        assert settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] is True

    def test_jwt_algorithm_hs256(self):
        """Verify HS256 signing algorithm."""
        from django.conf import settings
        assert settings.SIMPLE_JWT["ALGORITHM"] == "HS256"

    def test_jwt_bearer_auth_header(self):
        """Verify Bearer auth header type."""
        from django.conf import settings
        assert "Bearer" in settings.SIMPLE_JWT["AUTH_HEADER_TYPES"]

    def test_jwt_custom_serializer(self):
        """Verify custom tenant serializer is configured."""
        from django.conf import settings
        assert settings.SIMPLE_JWT["TOKEN_OBTAIN_SERIALIZER"] == \
            "api.serializers_auth.TenantTokenObtainPairSerializer"


# ── DRF Auth Config Tests ────────────────────────────────────

class TestDRFAuthConfig:
    """Test DRF authentication configuration."""

    def test_jwt_auth_is_primary(self):
        """Verify JWT is the first auth class (highest priority)."""
        from django.conf import settings
        auth_classes = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
        assert auth_classes[0] == "rest_framework_simplejwt.authentication.JWTAuthentication"

    def test_no_basic_auth(self):
        """Verify BasicAuthentication was removed (insecure)."""
        from django.conf import settings
        auth_classes = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
        assert "rest_framework.authentication.BasicAuthentication" not in auth_classes

    def test_session_auth_still_available(self):
        """Verify SessionAuthentication is kept as fallback."""
        from django.conf import settings
        auth_classes = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
        assert "rest_framework.authentication.SessionAuthentication" in auth_classes

    def test_api_key_auth_still_available(self):
        """Verify ApiKeyAuthentication is kept for service-to-service."""
        from django.conf import settings
        auth_classes = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
        assert "api.authentication.ApiKeyAuthentication" in auth_classes
