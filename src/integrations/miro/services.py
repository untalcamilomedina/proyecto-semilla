from integrations.schemas import ERDSpec
from integrations.miro.client import MiroClient
from integrations.miro.adapters import MiroAdapter

class MiroService:
    """
    Business logic for Miro integration.
    """

    @staticmethod
    async def export_erd_to_board(token: str, board_id: str, spec: ERDSpec):
        """
        Takes a Canonical ERD Spec and draws it on a Miro Board.
        """
        client = MiroClient(token)
        
        # Simple layout algorithm (grid)
        x_start = 0
        y_start = 0
        x_spacing = 300
        y_spacing = 300
        cols = 4
        
        created_items = {} # SpecID -> MiroID

        # 1. Create Nodes (Tables)
        for i, entity in enumerate(spec.entities):
            col = i % cols
            row = i // cols
            
            x = x_start + (col * x_spacing)
            y = y_start + (row * y_spacing)
            
            # Use Adapter explicitly
            shape_data = MiroAdapter.entity_to_miro_shape(entity, x, y)
            
            # API Call
            miro_item = await client.create_shape(board_id, shape_data)
            created_items[entity.id] = miro_item.get("id")

        # 2. Create Connectors (Relationships)
        client = MiroClient(token)
        for rel in spec.relationships:
            source_miro_id = created_items.get(rel.source)
            target_miro_id = created_items.get(rel.target)
            
            if source_miro_id and target_miro_id:
                connector_data = MiroAdapter.relationship_to_connector(rel, source_miro_id, target_miro_id)
                await client.create_connector(board_id, connector_data)
        
        return {"status": "success", "items_created": len(created_items)}

    @staticmethod
    async def import_from_miro(token: str, board_id: str) -> ERDSpec:
        """
        Reads a Miro Board, finds ERD shapes, and reconstructs the Spec.
        """
        client = MiroClient(token)
        
        # 1. Fetch all items
        items = await client.get_board_items(board_id)
        
        entities = []
        relationships = []
        
        # Pass 1: Entities
        for item in items:
            if item.get("data", {}).get("shape") == "rectangle":
                try:
                    entity = MiroAdapter.miro_to_canonical(item)
                    entities.append(entity)
                except Exception:
                    continue
        
        # Pass 2: Connectors
        # We need to map Miro IDs to Canonical IDs if we were changing them, 
        # but for Import, the Canonical ID IS the Miro ID, so we are good.
        for item in items:
            if item.get("type") == "connector":
                try:
                    rel = MiroAdapter.connector_to_relationship(item)
                    if rel:
                        relationships.append(rel)
                except Exception:
                    continue

        return ERDSpec(entities=entities, relationships=relationships)
