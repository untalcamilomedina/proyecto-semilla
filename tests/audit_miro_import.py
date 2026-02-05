import pytest
from unittest.mock import AsyncMock, patch
from integrations.schemas import ERDSpec
from integrations.miro.services import MiroService

@pytest.mark.asyncio
async def test_import_erd_from_miro_flow():
    """
    Verifies the Import Flow: Client (Mock) -> Adapter (Regex) -> Service -> ERDSpec.
    """
    # 1. Mock External Data (Miro Shapes)
    mock_miro_items = [
        {
            "id": "shape-1",
            "data": {
                "shape": "rectangle",
                "content": "<strong>Users</strong><hr/><ul><li>🔒 id <span style='color:#888'>(uuid)</span></li><li>email <span style='color:#888'>(string)</span></li></ul>"
            }
        },
        {
            "id": "shape-2",
            "data": {
                "shape": "rectangle",
                "content": "<strong>Orders</strong><hr/><ul><li>price <span style='color:#888'>(int)</span></li></ul>"
            }
        },
        {
            "id": "connector-1",
            "data": {} # Ignoring connectors for now as per implementation
        }
    ]

    # 2. Mock Internal Components
    with patch("integrations.miro.services.MiroClient") as MockClient:
        mock_instance = MockClient.return_value
        # Mock get_board_items
        mock_instance.get_board_items = AsyncMock(return_value=mock_miro_items)

        # 3. Execute Service Logic
        spec = await MiroService.import_from_miro("fake_token", "board_123")

        # 4. Assertions (Audit)
        assert isinstance(spec, ERDSpec)
        assert len(spec.entities) == 2
        
        # Verify Parsing Logic (Adapter Check)
        users = next(e for e in spec.entities if e.name == "Users")
        assert len(users.attributes) == 2
        assert users.attributes[0].name == "id"
        assert users.attributes[0].pk == True
        assert users.attributes[0].type == "uuid"
        
        assert users.attributes[1].name == "email"
        assert users.attributes[1].pk == False
        
        print("\n✅ API First Audit: Miro Import logic correctly parses HTML shapes.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_import_erd_from_miro_flow())
