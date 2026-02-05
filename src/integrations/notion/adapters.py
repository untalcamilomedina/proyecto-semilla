from typing import Dict, Any, List, Optional
from integrations.schemas import ERDSpec, FlowSpec, FlowNode, FlowEdge

class NotionAdapter:
    """
    Adapter to translate between Notion API structures and Canonical Models.
    """

    @staticmethod
    def database_to_entity(database: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a Notion Database object to a simplified Entity structure
        for the ERDSpec.
        """
        db_id = database.get("id")
        title_obj = database.get("title", [])
        name = "Untitled"
        if title_obj and len(title_obj) > 0:
            name = title_obj[0].get("plain_text", "Untitled")

        properties = database.get("properties", {})
        attributes = []
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type", "unknown")
            attributes.append({
                "name": prop_name,
                "type": prop_type,
                "pk": prop_type == "title",
                "nullable": True
            })

        return {
            "id": db_id,
            "name": name,
            "attributes": attributes
        }

    @staticmethod
    def page_to_node(page: Dict[str, Any]) -> FlowNode:
        """
        Maps a Notion Page to a Node in the FlowSpec.
        Useful if we interpret pages as steps in a process.
        """
        page_id = page.get("id")
        props = page.get("properties", {})
        
        # Try to find a 'Name' or 'Title' property
        label = "Untitled"
        for key, val in props.items():
            if val.get("type") == "title":
                content = val.get("title", [])
                if content:
                    label = content[0].get("plain_text", "Untitled")
                break
        
        return FlowNode(
            id=page_id,
            type="process", # Mapped to valid Literal
            label=label,
            meta={"url": page.get("url"), "original_type": "page"}
        )
