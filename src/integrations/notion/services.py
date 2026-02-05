from typing import List, Optional
from integrations.schemas import ERDSpec, ERDEntity, FlowSpec
from integrations.notion.client import NotionClient
from integrations.notion.adapters import NotionAdapter
from billing.metering import MeteringService

class NotionService:
    """
    Business logic for interaction with Notion workspaces.
    """

    @staticmethod
    async def scan_databases(token: str, tenant=None) -> ERDSpec:
        """
        Scans all databases in the workspace and returns a Canoncial ERD Spec.
        """
        # 0. Check Limits (if tenant provided)
        if tenant:
            # Check limits synchronously (Django ORM) before async work
            # Note: In pure async views, use database_sync_to_async wrapper
            # For now assuming this runs in a sync context or safe thread
            MeteringService.check_and_track_request(tenant, "requests")

        client = NotionClient(token)
        try:
            # 1. Fetch all databases
            notion_dbs = await client.search_databases()
            
            # 2. Convert to Canonical Entities
            entities = []
            for db in notion_dbs:
                entity_data = NotionAdapter.database_to_entity(db)
                entities.append(ERDEntity(**entity_data))
            
            # 3. Return Spec
            return ERDSpec(entities=entities, relationships=[])
        finally:
            await client.close()

    @staticmethod
    async def apply_erd(token: str, parent_page_id: str, spec: ERDSpec, tenant=None) -> List[str]:
        """
        Applies an ERD Spec to Notion by creating databases.
        """
        if tenant:
            MeteringService.check_and_track_request(tenant, "diagrams")

        client = NotionClient(token)
        created_ids = []
        try:
            for entity in spec.entities:
                properties = {"Name": {"title": {}}}
                for attr in entity.attributes:
                    if attr.is_primary: continue
                    if attr.type == "text": properties[attr.name] = {"rich_text": {}}
                    elif attr.type == "number": properties[attr.name] = {"number": {}}
                    elif attr.type == "select": properties[attr.name] = {"select": {}}
                    elif attr.type == "date": properties[attr.name] = {"date": {}}

                result = await client.create_database(
                    parent_page_id=parent_page_id,
                    schema={
                        "title": [{"type": "text", "text": {"content": entity.name}}],
                        "properties": properties
                    }
                )
                created_ids.append(result["id"])
            return created_ids
        finally:
            await client.close()

    @staticmethod
    async def apply_flow(token: str, parent_page_id: str, spec: FlowSpec, tenant=None) -> str:
        """
        Converts a FlowSpec (Miro) into a Notion Database (Kanban Board).
        """
        if tenant:
             MeteringService.check_and_track_request(tenant, "requests")

        client = NotionClient(token)
        try:
            # 1. Create Database for the Flow
            # We map 'Stages' (if any) to a Status/Select property
            properties = {
                "Name": {"title": {}},
                "Stage": {"select": {"options": [{"name": "To Do", "color": "red"}, {"name": "Done", "color": "green"}]}},
                "Type": {"select": {}}
            }

            result = await client.create_database(
                parent_page_id=parent_page_id,
                schema={
                    "title": [{"type": "text", "text": {"content": f"Flow: {spec.id}"}}],
                    "properties": properties
                }
            )
            
            # 2. Create Pages for each Node (Not Implemented in Client yet, but logic is here)
            # await client.create_page(database_id=result["id"], properties={...})

            return result["id"]
        finally:
            await client.close()
