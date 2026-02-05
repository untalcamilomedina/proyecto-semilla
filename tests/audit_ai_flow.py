import pytest
import json
from unittest.mock import patch, AsyncMock
from integrations.models import UserAPIKey
from integrations.ai.services import AIService
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_translate_flow_mocked():
    """
    Verifies that the AIService logic correctly:
    1. Decrypts the user key.
    2. Calls the GeminiClient (Mocked).
    3. Parses the returned Markdown/JSON.
    """
    # 1. Setup User & Key
    import uuid
    uid = str(uuid.uuid4())[:8]
    user = await User.objects.acreate(
        username=f"ai_test_{uid}", 
        email=f"ai_{uid}@example.com", 
        password="password"
    )
    
    # Create key synchronously for simplicity of model methods, or wrapped
    # We'll use sync creation here inside async test (allowed with django_db)
    api_key = await UserAPIKey.objects.acreate(user=user, provider="gemini", label="Test Key")
    
    # Manually call set_key logic (sync method, so we can't await it strictly without sync_to_async 
    # but in pytest-django async context, we can misuse if careful, or use sync_to_async)
    from asgiref.sync import sync_to_async
    await sync_to_async(api_key.set_key)("my-secret-gemini-key")
    await sync_to_async(api_key.save)()
    
    # 2. Mock Gemini Response
    mock_json = {
        "entities": [
            {"id": "uuid-1", "name": "Author", "attributes": [{"name": "id", "type": "uuid", "pk": True}]}
        ],
        "relationships": []
    }
    mock_text = f"```json\n{json.dumps(mock_json)}\n```"
    
    # 3. Patch the GeminiClient
    with patch("integrations.ai.services.GeminiClient") as MockClientClass:
        mock_instance = MockClientClass.return_value
        mock_instance.generate_content = AsyncMock(return_value=mock_text)
        
        # 4. Assert Key passed to Client was DECRYPTED
        # We need to run the service
        result = await AIService.translate_text_to_erd(user, "Analyze this")
        
        # Verify result is parsed dict
        assert result["entities"][0]["name"] == "Author"
        
        # Verify Client init API key
        MockClientClass.assert_called_with(api_key="my-secret-gemini-key")
        print("\n✅ AI Service successfully decrypted key and parsed JSON response.")
