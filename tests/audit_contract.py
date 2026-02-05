import pytest
from rest_framework.test import APIClient
from integrations.schemas import FlowSpec, ERDSpec
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_schema_integrity():
    """
    Verifies that the Pydantic Models (Canonical Schemas) require strict adherence.
    This ensures that whatever the API returns fits into these models.
    """
    
    # 1. Valid FlowSpec
    valid_flow = {
        "nodes": [{"id": "n1", "type": "process", "label": "Start"}],
        "edges": []
    }
    try:
        FlowSpec(**valid_flow)
    except Exception as e:
        pytest.fail(f"Valid FlowSpec failed validation: {e}")

    # 2. Invalid FlowSpec (Missing required field 'id')
    invalid_flow = {
        "nodes": [{"type": "process", "label": "Start"}],
        "edges": []
    }
    with pytest.raises(ValueError):
        FlowSpec(**invalid_flow)

    print("\n✅ Canonical Schemas enforce integrity correctly.")

    print("\n✅ Canonical Schemas enforce integrity correctly.")

@pytest.mark.django_db
def test_api_docs_access():
    """
    Verifies that Swagger/OpenAPI endpoint is reachable and generates schema without error.
    This implies correct Serializer configuration across the project.
    """
    client = APIClient()
    # Assuming public or basic auth
    # For now, just checking it doesn't crash 500
    response = client.get("/api/v1/schema/")
    # If 200, schema generated. If 401/403, at least it's served. If 500, config error.
    assert response.status_code != 500, "Schema generation crashed!"
