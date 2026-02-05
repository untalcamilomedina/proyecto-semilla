import pytest
from unittest.mock import AsyncMock, patch
from integrations.schemas import ERDSpec, ERDEntity, ERDAttribute
from integrations.miro.services import MiroService

@pytest.mark.asyncio
async def test_export_erd_to_miro_flow():
    """
    Verifies the Export Flow: Service -> Adapter -> Client -> Miro API.
    Mocks the actual Miro API call to test logic in isolation.
    """
    # 1. Setup Canonical Payload (What we want to export)
    spec = ERDSpec(
        entities=[
            ERDEntity(
                id="e1", 
                name="Users", 
                attributes=[
                    ERDAttribute(name="id", type="uuid", pk=True),
                    ERDAttribute(name="email", type="email", unique=True)
                ]
            )
        ],
        relationships=[]
    )

    # 2. Mock Internal Components
    with patch("integrations.miro.services.MiroClient") as MockClient:
        # Setup Mock Client instance
        mock_instance = MockClient.return_value
        # Mock create_shape to return a fake Miro Item ID
        mock_instance.create_shape = AsyncMock(return_value={"id": "shape-rectangle-123"})

        # 3. Execute Service Logic
        result = await MiroService.export_erd_to_board("fake_token", "board_123", spec)

        # 4. Assertions (Audit)
        assert result["status"] == "success"
        assert result["items_created"] == 1
        
        # Verify the Client was called with correct transformed data (Adapter logic check)
        mock_instance.create_shape.assert_called_once()
        call_args = mock_instance.create_shape.call_args[0]
        board_id_arg = call_args[0]
        payload_arg = call_args[1]

        assert board_id_arg == "board_123"
        assert payload_arg["data"]["shape"] == "rectangle"
        # Check if the HTML content contains our attributes
        assert "Users" in payload_arg["data"]["content"]
        assert "email" in payload_arg["data"]["content"]

        print("\n✅ API First Audit: Miro Export Service correctly transforms ERD Spec to Miro Shapes.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_export_erd_to_miro_flow())
