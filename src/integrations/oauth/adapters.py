from django.conf import settings
import httpx
import base64
from typing import Dict, Any

class OAuthProvider:
    """
    Base class for OAuth 2.0 Providers.
    """
    def get_authorization_url(self, state: str) -> str:
        raise NotImplementedError

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """
        Exchanges temporary code for access token.
        Returns dict containing 'access_token' and optional 'refresh_token'.
        """
        raise NotImplementedError

class NotionOAuthProvider(OAuthProvider):
    # https://developers.notion.com/docs/authorization
    AUTH_URL = "https://api.notion.com/v1/oauth/authorize"
    TOKEN_URL = "https://api.notion.com/v1/oauth/token"
    
    def __init__(self):
        self.client_id = settings.NOTION_CLIENT_ID
        self.client_secret = settings.NOTION_CLIENT_SECRET
        self.redirect_uri = f"{settings.DOMAIN_BASE}/api/v1/integrations/notion/callback"

    def get_authorization_url(self, state: str) -> str:
        # Notion uses Basic Auth for exchange, but query params for auth URL
        url = (
            f"{self.AUTH_URL}?"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"owner=user&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}"
        )
        return url

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        # Notion requires Basic Auth header with ClientID:ClientSecret
        creds = f"{self.client_id}:{self.client_secret}"
        encoded_creds = base64.b64encode(creds.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/json"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, headers=headers, json=data)
            resp.raise_for_status()
            return resp.json()

class MiroOAuthProvider(OAuthProvider):
    # https://developers.miro.com/docs/getting-started-with-oauth
    AUTH_URL = "https://miro.com/oauth/authorize"
    TOKEN_URL = "https://api.miro.com/v1/oauth/token"
    
    def __init__(self):
        self.client_id = settings.MIRO_CLIENT_ID
        self.client_secret = settings.MIRO_CLIENT_SECRET
        self.redirect_uri = f"{settings.DOMAIN_BASE}/api/v1/integrations/miro/callback"

    def get_authorization_url(self, state: str) -> str:
        url = (
            f"{self.AUTH_URL}?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}&"
            f"team_id=30744573523456789" # Optional: team context
        )
        return url

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data)
            resp.raise_for_status()
            return resp.json()

def get_provider(name: str) -> OAuthProvider:
    if name == "notion":
        return NotionOAuthProvider()
    elif name == "miro":
        return MiroOAuthProvider()
    raise ValueError(f"Unknown provider: {name}")
