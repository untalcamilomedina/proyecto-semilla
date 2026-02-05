import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Async Client for Google Gemini API (REST).
    Uses 'httpx' for non-blocking I/O.
    """
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        
    async def generate_content(self, prompt: str) -> str:
        """
        Sends a prompt to Gemini and returns the text response.
        """
        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2, # Low temp for deterministic code/json generation
                "maxOutputTokens": 4000
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract text from response structure
                # { "candidates": [ { "content": { "parts": [ { "text": "..." } ] } } ] }
                candidates = result.get("candidates", [])
                if not candidates:
                    raise ValueError("No candidates returned from Gemini")
                    
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    return ""
                    
                return parts[0].get("text", "")
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Gemini API Error: {e.response.text}")
                raise ValueError(f"Gemini API Error: {e.response.status_code}")
            except Exception as e:
                logger.exception("Gemini Client Error")
                raise
