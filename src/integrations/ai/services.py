import json
import re
from integrations.models import UserAPIKey
from .gemini_client import GeminiClient

class AIService:
    """
    Business logic for AI capabilities.
    Handles Key Decryption and Prompt Engineering.
    """
    
    SYSTEM_PROMPT_ERD = """
    You are an expert Data Architect. 
    Your task is to convert the following user description into a Canonical ERD Spec (JSON).
    
    Output Format Rules:
    1. Return ONLY valid JSON. No markdown formatting (no ```json).
    2. Structure:
    {
      "entities": [
        {
          "id": "uuid", 
          "name": "TableName", 
          "attributes": [
             {"name": "id", "type": "uuid", "pk": true},
             {"name": "field", "type": "string"}
          ]
        }
      ],
      "relationships": []
    }
    3. Infer data types correctly (string, integer, boolean, uuid, datetime).
    """

    @staticmethod
    async def translate_text_to_erd(user, text: str) -> dict:
        """
        Orchestrate the translation flow.
        """
        # 1. Retrieve & Decrypt Key
        try:
            api_key_obj = await UserAPIKey.objects.aget(user=user, provider=UserAPIKey.PROVIDER_GEMINI)
            decrypted_key = api_key_obj.get_key()
        except UserAPIKey.DoesNotExist:
            raise ValueError("No Gemini API Key provided. Please configure it in settings.")
            
        # 2. Call Gemini
        client = GeminiClient(api_key=decrypted_key)
        full_prompt = f"{AIService.SYSTEM_PROMPT_ERD}\n\nUser Description:\n{text}"
        
        raw_response = await client.generate_content(full_prompt)
        
        # 3. Clean & Parse JSON
        try:
            # Remove Markdown code blocks if Gemini ignores the instruction
            clean_json = re.sub(r"```json|```", "", raw_response).strip()
            return json.loads(clean_json)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse AI response as JSON: {raw_response[:100]}...")
