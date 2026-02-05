import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestSecurityAudit:
    """
    Security Audit verifying Authentication & Authorization enforcement.
    Uses 'test-api-endpoint' skill principles.
    """
    
    def test_anonymous_access_denied_notion(self, api_client):
        """
        GIVEN no authentication
        WHEN accessing Notion Integration
        THEN return 401/403
        """
        url = "/api/v1/integrations/notion/scan/" # Assuming simple URL structure or reverse
        response = api_client.post(url, {}) # POST requires auth
        assert response.status_code in [401, 403], f"Notion Scan endpoint MUST be protected. Got {response.status_code}"

    def test_anonymous_access_denied_ai(self, api_client):
        """
        GIVEN no authentication
        WHEN accessing AI Translate (Costly)
        THEN return 401/403
        """
        url = "/api/v1/integrations/ai/translate/"
        response = api_client.post(url, {})
        assert response.status_code in [401, 403], f"AI Translate endpoint MUST be protected. Got {response.status_code}"

    def test_authenticated_access_allowed(self, api_client):
        """
        GIVEN authenticated user
        WHEN accessing protected endpoints (with bad data to provoke validation error, not auth error)
        THEN return 400 (Validation Error), NOT 401/403
        """
        import uuid
        uid = str(uuid.uuid4())[:8]
        user = User.objects.create_user(username=f"audit_{uid}", email=f"audit_{uid}@test.com", password="password")
        api_client.force_authenticate(user=user)
        
        # Notion
        resp_notion = api_client.post("/api/v1/integrations/notion/scan/", {})
        assert resp_notion.status_code == 400, "Should pass auth and fail validation"
        
        # AI
        resp_ai = api_client.post("/api/v1/integrations/ai/translate/", {})
        assert resp_ai.status_code == 400, "Should pass auth and fail validation"
