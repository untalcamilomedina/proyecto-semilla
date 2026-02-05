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
