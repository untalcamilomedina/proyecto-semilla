from typing import Any, Dict, List
from integrations.schemas import ERDEntity

class MiroAdapter:
    """
    Transforms Canonical Models (ERD/Flow) into Miro Shapes.
    """

    @staticmethod
    def entity_to_miro_shape(entity: ERDEntity, x: float = 0, y: float = 0) -> Dict[str, Any]:
        """
        Maps an ERDEntity to a Miro 'shape' (Rectangle representing a Table).
        Includes HTML content to list attributes visually.
        """
        # Build HTML content for the table visualization
        rows_html = "".join(
            f"<li>{'🔒 ' if attr.pk else ''}{attr.name} <span style='color:#888'>({attr.type})</span></li>"
            for attr in entity.attributes
        )
        
        content = f"""
        <strong>{entity.name}</strong>
        <hr/>
        <ul style="list-style-type: none; padding-left: 0;">
            {rows_html}
        </ul>
        """
        
        return {
            "data": {
                "shape": "rectangle",
                "content": content,
            },
            "style": {
                "fillColor": "#ffffff",
                "textAlign": "left",
                "textAlignVertical": "top"
            },
            "position": {
                "x": x,
                "y": y
            },
            "geometry": {
                "width": 200,
                "height": 50 + (len(entity.attributes) * 20)
            }
        }

    @staticmethod
    def miro_to_canonical(miro_item: Dict[str, Any]) -> ERDEntity:
        """
        Maps a Miro item (shape) back to a Canonical Entity.
        Parses the HTML content to extract Name and Attributes.
        """
        import re
        
        data = miro_item.get("data", {})
        content = data.get("content", "")
        
        # 1. Extract Name (Bold text)
        # Match <strong>Name</strong>
        name_match = re.search(r"<strong>(.*?)</strong>", content)
        name = name_match.group(1) if name_match else "Untitled"
        
        # 2. Extract Attributes
        # Match <li>...</li>
        attributes = []
        li_items = re.findall(r"<li>(.*?)</li>", content)
        
        for li in li_items:
            # Check PK
            is_pk = "🔒" in li
            clean_li = li.replace("🔒 ", "").strip()
            
            # Extract Type from span
            # Example: id <span...> (uuid)</span>
            type_match = re.search(r"\((.*?)\)</span>", clean_li)
            # Remove span from name part
            name_part = re.sub(r"<span.*?>.*?</span>", "", clean_li).strip()
            
            attr_type = type_match.group(1) if type_match else "string"
            
            attributes.append({
                "name": name_part,
                "type": attr_type,
                "pk": is_pk
            })
            
        return ERDEntity(
            id=miro_item.get("id"),
            name=name,
            attributes=attributes
        )

    @staticmethod
    def relationship_to_connector(rel: ERDRelationship, source_item_id: str, target_item_id: str) -> Dict[str, Any]:
        """
        Creates a Miro Connector (Line) between two shapes.
        """
        return {
            "data": {
                "startItem": {"id": source_item_id},
                "endItem": {"id": target_item_id},
                "shape": "elbowed", # Orthogonal lines
                "captions": [{"content": rel.cardinality}] if rel.cardinality else []
            },
            "style": {
                "strokeColor": "#000000",
                "strokeWidth": 2,
                "endArrow": "filled_triangle" # Visual cue for direction
            }
        }

    @staticmethod
    def connector_to_relationship(connector: Dict[str, Any]) -> Optional[ERDRelationship]:
        """
        Maps a Miro Connector to an ERD Relationship.
        """
        data = connector.get("data", {})
        start_item = data.get("startItem", {}).get("id")
        end_item = data.get("endItem", {}).get("id")
        
        if not start_item or not end_item:
            return None
            
        captions = data.get("captions", [])
        cardinality = "1:N" # Default
        if captions:
            # Try to grab content from first caption
            cardinality = captions[0].get("content", "1:N")

        return ERDRelationship(
            id=connector.get("id"),
            source=start_item, # Miro ID, will need mapping to Canonical ID if IDs change
            target=end_item,
            cardinality=cardinality
        )
