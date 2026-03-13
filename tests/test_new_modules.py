"""
Tests for common.encryption module.

Tests Fernet-based encryption/decryption and the EncryptedCharField.
"""

import pytest
from django.test import TestCase, override_settings

from common.encryption import decrypt_value, encrypt_value


class TestEncryption(TestCase):
    """Test Fernet encryption utilities."""

    def test_encrypt_empty_string_returns_empty(self):
        """Empty strings should not be encrypted."""
        assert encrypt_value("") == ""

    def test_encrypt_returns_prefixed_ciphertext(self):
        """Encrypted values should be prefixed with 'enc::'."""
        result = encrypt_value("my-secret-api-key")
        assert result.startswith("enc::")
        assert "my-secret-api-key" not in result

    def test_decrypt_returns_original_plaintext(self):
        """Decryption should return the original plaintext."""
        original = "super-secret-key-12345"
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        assert decrypted == original

    def test_decrypt_non_encrypted_returns_as_is(self):
        """Non-encrypted values should be returned unchanged."""
        plaintext = "not-encrypted"
        assert decrypt_value(plaintext) == plaintext

    def test_decrypt_empty_returns_empty(self):
        """Empty string decryption should return empty."""
        assert decrypt_value("") == ""
        assert decrypt_value(None) is None

    def test_roundtrip_special_characters(self):
        """Encryption should handle special characters correctly."""
        special = "key_with_特殊文字_и_символы_🔐"
        encrypted = encrypt_value(special)
        decrypted = decrypt_value(encrypted)
        assert decrypted == special

    def test_different_inputs_produce_different_ciphertexts(self):
        """Different inputs should produce different encrypted outputs."""
        enc1 = encrypt_value("key-alpha")
        enc2 = encrypt_value("key-beta")
        assert enc1 != enc2

    def test_same_input_produces_different_ciphertexts(self):
        """Same input encrypted twice should produce different ciphertexts (Fernet uses timestamps)."""
        enc1 = encrypt_value("same-key")
        enc2 = encrypt_value("same-key")
        # Fernet includes timestamp, so same plaintext → different ciphertext
        assert enc1 != enc2
        # But both should decrypt to the same value
        assert decrypt_value(enc1) == decrypt_value(enc2) == "same-key"


class TestRLS:
    """Test RLS SQL generation (unit tests, no DB needed)."""

    def test_enable_rls_generates_statements(self):
        from common.rls import enable_rls_sql, TENANT_SCOPED_TABLES

        statements = enable_rls_sql()
        # Each table generates: ENABLE, FORCE, DROP+CREATE isolation, DROP+CREATE bypass = 6
        assert len(statements) == len(TENANT_SCOPED_TABLES) * 6

    def test_disable_rls_generates_statements(self):
        from common.rls import disable_rls_sql, TENANT_SCOPED_TABLES

        statements = disable_rls_sql()
        # Each table generates: DROP isolation, DROP bypass, DISABLE = 3
        assert len(statements) == len(TENANT_SCOPED_TABLES) * 3

    def test_enable_rls_contains_correct_tables(self):
        from common.rls import enable_rls_sql

        sql = "\n".join(enable_rls_sql())
        assert "core_role" in sql
        assert "billing_subscription" in sql
        assert "cms_contentpage" in sql
        assert "lms_course" in sql
        assert "community_space" in sql
        assert "mcp_mcpserver" in sql

    def test_special_fk_column_for_onboarding(self):
        from common.rls import get_fk_column

        assert get_fk_column("core_onboardingstate") == "tenant_id"
        assert get_fk_column("core_role") == "organization_id"


@pytest.mark.django_db
class TestCMSModels:
    """Test MDX CMS models."""

    def test_category_auto_slug(self):
        from cms.models import Category
        from multitenant.models import Tenant

        tenant = Tenant.objects.create(name="Test CMS", slug="test-cms", schema_name="test_cms")
        cat = Category(organization=tenant, name="My Category")
        cat.save()
        assert cat.slug == "my-category"

    def test_content_page_auto_slug(self):
        from cms.models import ContentPage
        from multitenant.models import Tenant

        tenant = Tenant.objects.create(name="Test CMS2", slug="test-cms2", schema_name="test_cms2")
        page = ContentPage(organization=tenant, title="Hello World Post")
        page.save()
        assert page.slug == "hello-world-post"

    def test_content_page_status_choices(self):
        from cms.models import ContentPage

        assert ContentPage.Status.DRAFT == "draft"
        assert ContentPage.Status.PUBLISHED == "published"
        assert ContentPage.Status.ARCHIVED == "archived"

    def test_media_asset_creation(self):
        from cms.models import MediaAsset
        from multitenant.models import Tenant

        tenant = Tenant.objects.create(name="Test CMS3", slug="test-cms3", schema_name="test_cms3")
        asset = MediaAsset.objects.create(
            organization=tenant,
            filename="test.png",
            mime_type="image/png",
            size_bytes=1024,
        )
        assert str(asset) == "test.png"
        assert asset.size_bytes == 1024
