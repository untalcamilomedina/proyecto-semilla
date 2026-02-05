from typing import List, Optional
from integrations.schemas import ERDSpec, ERDEntity
from integrations.notion.client import NotionClient
from integrations.notion.adapters import NotionAdapter

class NotionService:
    """
    Business logic for interaction with Notion workspaces.
    """

    @staticmethod
    async def scan_databases(token: str) -> ERDSpec:
        """
        Scans all databases in the workspace and returns a Canoncial ERD Spec.
        """
        client = NotionClient(token)
        try:
            # 1. Fetch all databases
            notion_dbs = await client.search_databases()
            
            # 2. Convert to Canonical Entities
            entities = []
            for db in notion_dbs:
                entity_data = NotionAdapter.database_to_entity(db)
                # Map adapter output to ERDEntity schema
                # Adapter returns 'attributes' list of dicts. 
                # We need to ensure keys match ERDAttribute or we do it here.
                # Let's trust Adapter returns valid dicts for ERDEntity construction
                entities.append(ERDEntity(**entity_data))
            
            # 3. Return Spec
            return ERDSpec(entities=entities, relationships=[])
        finally:
            await client.close()

    @staticmethod
    async def apply_erd(token: str, parent_page_id: str, spec: ERDSpec) -> List[str]:
        """
        Applies an ERD Spec to Notion by creating databases.
        Returns list of created database IDs.
        """
        client = NotionClient(token)
        created_ids = []
        try:
            for entity in spec.entities:
                # 1. Construct Notion Schema (Simplified)
                # In a real scenario, we'd use an adapter to go Canonical -> Notion Payload
                properties = {
                    "Name": {"title": {}} # Default title
                }
                
                # Naive implementation of attribute creation
                for attr in entity.attributes:
                    if attr.is_primary:
                        continue # Title is handled
                    
                    # Mapping constraints (simplified for MVP)
                    if attr.type == "text":
                        properties[attr.name] = {"rich_text": {}}
                    elif attr.type == "number":
                        properties[attr.name] = {"number": {}}
                    elif attr.type == "select":
                        properties[attr.name] = {"select": {}}
                    # ... add more types as needed

                # 2. Create DB
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
