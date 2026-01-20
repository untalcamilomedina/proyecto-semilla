import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.models import OnboardingState


@pytest.mark.django_db
class TestOnboardingAPI:
    def test_start_onboarding(self, api_client):
        """Test starting onboarding via API creates tenant and user."""
        payload = {
            "org_name": "Test Org API",
            "subdomain": "testapi",
            "admin_email": "admin@testapi.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        response = api_client.post("/api/v1/onboarding/start/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert "tenant_id" in response.data
        assert "state_id" in response.data

        # Verify state created
        state = OnboardingState.objects.get(id=response.data["state_id"])
        assert state.owner_email == "admin@testapi.com"
        assert state.tenant.slug == "testapi"
        assert state.current_step == 2

    def test_modules_step(self, authenticated_client, user, tenant):
        """Test setting modules via API."""
        # Create initial state manually since we are skipping step 1 in this test
        # But we need OnboardingState linked to user
        from core.models import OnboardingState
        from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context
        
        with schema_context(PUBLIC_SCHEMA_NAME):
            OnboardingState.objects.create(
                tenant=tenant,
                owner_email=user.email,
                current_step=2,
            )

        payload = {"modules": ["cms", "lms"]}
        response = authenticated_client.post("/api/v1/onboarding/modules/", payload)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify
        with schema_context(PUBLIC_SCHEMA_NAME):
            state = OnboardingState.objects.get(tenant=tenant)
            assert "cms" in state.data["modules"]
            assert state.current_step > 2

    def test_start_onboarding_invalid_password(self, api_client):
        """Test validation error."""
        payload = {
            "org_name": "Test Org API",
            "subdomain": "testapi2",
            "admin_email": "admin@testapi2.com",
            "password": "password123",
            "confirm_password": "password_mismatch",
        }
        response = api_client.post("/api/v1/onboarding/start/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirm_password" in response.data["details"]
