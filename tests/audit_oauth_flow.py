import pytest
from django.conf import settings
from integrations.models import IntegrationConnection
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_integration_connection_encryption():
    """
    Verifies that tokens are encrypted in the DB and decrypted on access.
    """
    # 1. Create User
    user = User.objects.create_user(username="test_auth_user", password="password")
    
    # 2. Basic Token Data
    raw_access_token = "access-token-secret-123"
    raw_refresh_token = "refresh-token-secret-456"
    
    # 3. Create Connection via Helper
    conn = IntegrationConnection(user=user, provider=IntegrationConnection.PROVIDER_NOTION)
    conn.set_token(raw_access_token, raw_refresh_token)
    conn.save()
    
    # 4. Verify DB Storage (Should NOT be plain text)
    conn.refresh_from_db()
    assert conn.access_token_enc != raw_access_token
    assert raw_access_token not in conn.access_token_enc # Should be encrypted string
    print(f"\n✅ Access Token Encrypted: {conn.access_token_enc[:10]}...")
    
    # 5. Verify Decryption
    decrypted_access = conn.get_token()
    decrypted_refresh = conn.get_refresh_token()
    
    assert decrypted_access == raw_access_token
    assert decrypted_refresh == raw_refresh_token
    print(f"✅ Access Token Decrypted: {decrypted_access}")

if __name__ == "__main__":
    # Standard boilerplate to run Django test directly
    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    django.setup()
    
    # Running via pytest runner logic manually for simplicity or just run via pytest command
    print("Use 'pytest' to run this test properly within the container.")
