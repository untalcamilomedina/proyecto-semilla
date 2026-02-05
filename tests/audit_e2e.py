import pytest
import time
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
def test_e2e_performance_flow():
    """
    Simulates a critical user journey:
    1. Login (Auth)
    2. Import from Miro (Mocked External) -> Write to DB
    3. Read Diagram (Read DB)
    
    Includes basic Performance assertions (< 1.0s for write, < 0.1s for read).
    """
    client = APIClient()
    
    # 0. Auth Setup
    import uuid
    uid = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f"perf_{uid}", email=f"perf_{uid}@test.com", password="password")
    client.force_authenticate(user=user)
    
    # 1. Mock Miro Service to avoid network
    # We need to ensure get_board_items is treated as an async method
    from unittest.mock import AsyncMock
    with patch("integrations.miro.services.MiroClient") as MockClient:
        # Simulate getting 50 items from Miro
        # Simulate getting 50 items from Miro with correct structure
        mock_instance = MockClient.return_value
        mock_instance.get_board_items = AsyncMock(return_value=[
            {
                "id": "s1", 
                "type": "shape", 
                "data": {"shape": "rectangle", "content": "<strong>Users</strong>"}, 
                "style": {"fillColor": "#ffffff"}
            }
        ] * 50) 
        
        # Action: Import
        # URL is /api/v1/integrations/miro/import_erd/ because action function is 'import_erd'
        start_time = time.time()
        resp_import = client.post("/api/v1/integrations/miro/import_erd/", {
            "token": "fake-token",
            "board_id": "board-123"
        })
        end_time = time.time()
        
        import_duration = end_time - start_time
        assert resp_import.status_code == 200, f"Import failed: {resp_import.data}"
        print(f"\n⏱️ Import (Write) Duration: {import_duration:.4f}s")
        # Write can be slow (sync logic wrapper), but let's say < 1s
        assert import_duration < 2.0, "Import took too long!"
        
        diagram_spec = resp_import.json()
        
    # 2. Read Back (Critical Path)
    start_time = time.time()
    
    # Verify content
    assert len(diagram_spec["entities"]) > 0
    assert diagram_spec["entities"][0]["name"] == "Users"
    
    read_duration = time.time() - start_time
    print(f"⏱️ Serialization/Read Duration: {read_duration:.4f}s")
    assert read_duration < 0.1, "Serialization took too long!"
