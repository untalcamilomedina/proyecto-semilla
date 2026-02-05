import logging
from typing import Any, Dict, List, Optional
from notion_client import AsyncClient
from notion_client.errors import APIResponseError

logger = logging.getLogger(__name__)

class NotionClient:
    """
    Wrapper around notion_client.AsyncClient to provide robust error handling
    and simplified methods for our specific use cases.
    """

    def __init__(self, token: str):
        self.client = AsyncClient(auth=token)

    async def validate_token(self) -> Dict[str, Any]:
        """
        Validates the token by fetching the bot user info.
        """
        try:
            return await self.client.users.me()
        except APIResponseError as e:
            logger.error(f"Notion Token Validation Failed: {e}")
            raise e

    async def search_databases(self) -> List[Dict[str, Any]]:
        """
        Scans the workspace for all accessible Databases.
        """
        try:
            results = []
            has_more = True
            cursor = None

            while has_more:
                response = await self.client.search(
                    filter={"value": "database", "property": "object"},
                    start_cursor=cursor,
                    page_size=100
                )
                results.extend(response.get("results", []))
                has_more = response.get("has_more", False)
                cursor = response.get("next_cursor")
            
            return results
        except APIResponseError as e:
            logger.error(f"Failed to search databases: {e}")
            raise e

    async def get_database(self, database_id: str) -> Dict[str, Any]:
        """
        Retrieves a specific database by ID.
        """
        try:
            return await self.client.databases.retrieve(database_id=database_id)
        except APIResponseError as e:
            logger.error(f"Failed to get database {database_id}: {e}")
            raise e

    async def create_database(self, parent_page_id: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new database in Notion.
        """
        try:
            return await self.client.databases.create(
                parent={"page_id": parent_page_id},
                **schema
            )
        except APIResponseError as e:
            logger.error(f"Failed to create database: {e}")
            raise e

    async def update_database(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing database (e.g. adding properties).
        """
        try:
            return await self.client.databases.update(
                database_id=database_id,
                properties=properties
            )
        except APIResponseError as e:
            logger.error(f"Failed to update database {database_id}: {e}")
            raise e

    async def close(self):
        await self.client.aclose()
