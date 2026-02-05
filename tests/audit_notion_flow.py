import pytest
from unittest.mock import AsyncMock, patch
from integrations.schemas import ERDSpec, ERDEntity
from integrations.notion.services import NotionService

@pytest.mark.asyncio
async def test_scan_databases_flow():
    """
    Verifies the Scan Flow: Service -> Client -> Adapter -> Canonical Model.
    Mocks the actual Notion API call to test logic in isolation (API First).
    """
    # 1. Mock Data (Notion API Response)
    mock_notion_dbs = [
        {
            "id": "db-123",
            "title": [{"plain_text": "Projects"}],
            "object": "database",
            "properties": {
                "Name": {"type": "title"},
                "Status": {"type": "select"}
            }
        }
    ]

    # 2. Mock Internal Components
    with patch("integrations.notion.services.NotionClient") as MockClient:
        # Setup Mock Client instance
        mock_instance = MockClient.return_value
        mock_instance.search_databases = AsyncMock(return_value=mock_notion_dbs)
        mock_instance.close = AsyncMock()

        # 3. Execute Service Logic
        erdspec = await NotionService.scan_databases("fake_token")

        # 4. Assertions (Audit)
        assert isinstance(erdspec, ERDSpec)
        assert len(erdspec.entities) == 1
        
        entity = erdspec.entities[0]
        assert entity.id == "db-123"
        assert entity.name == "Projects"
        
        # Verify attributes mapped correctly
        titles = [attr for attr in entity.attributes if attr.name == "Name"]
        assert len(titles) == 1
        assert titles[0].pk == True  # Title should be PK based on adapter logic

        print("\n✅ API First Audit: Service Logic correctly transforms external API data to Canonical Schema.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scan_databases_flow())
