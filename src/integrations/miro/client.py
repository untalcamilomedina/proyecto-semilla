import logging
import httpx
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class MiroClient:
    """
    Wrapper around Miro REST API V2.
    """
    BASE_URL = "https://api.miro.com/v2"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_board(self, board_id: str) -> Dict[str, Any]:
        """
        Retrieves board metadata.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/boards/{board_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_board_items(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Fetches all items (nodes/connectors) from a board.
        Handles pagination automatically.
        """
        items = []
        cursor = None
        
        async with httpx.AsyncClient() as client:
            while True:
                params = {"limit": 50}
                if cursor:
                    params["cursor"] = cursor
                
                response = await client.get(
                    f"{self.BASE_URL}/boards/{board_id}/items",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                items.extend(data.get("data", []))
                
                cursor = data.get("links", {}).get("next")
                if not cursor:
                    break
                    
        return items

    async def create_shape(self, board_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a shape item on the board.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/boards/{board_id}/shapes",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def create_connector(self, board_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a connector (line/edge) between items.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/boards/{board_id}/connectors",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
