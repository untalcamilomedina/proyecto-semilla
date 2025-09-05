"""
Proyecto Semilla SDK Authentication - JWT token management
"""

import time
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta

from .exceptions import AuthenticationError, APIError


class AuthManager:
    """Manages authentication tokens and session state"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.user_info: Optional[Dict[str, Any]] = None

    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        """Set authentication tokens"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ProyectoSemilla-SDK/0.1.0'
        }

        if self.api_key:
            headers['X-API-Key'] = self.api_key
        elif self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'

        return headers

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at

    def needs_refresh(self) -> bool:
        """Check if token needs refresh (expires in < 5 minutes)"""
        if not self.token_expires_at:
            return False
        return datetime.now() > (self.token_expires_at - timedelta(minutes=5))

    def clear_tokens(self):
        """Clear all authentication data"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.user_info = None

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        return self.user_info

    def set_user_info(self, user_info: Dict[str, Any]):
        """Set current user information"""
        self.user_info = user_info

    async def refresh_access_token(self, client) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise AuthenticationError("No refresh token available")

        try:
            response = await client.post('/auth/refresh', json={
                'refresh_token': self.refresh_token
            })

            if response.status_code == 200:
                data = response.json()
                self.set_tokens(
                    data['access_token'],
                    data.get('refresh_token', self.refresh_token),
                    data.get('expires_in', 3600)
                )
                return True
            else:
                self.clear_tokens()
                raise AuthenticationError("Token refresh failed")

        except Exception as e:
            self.clear_tokens()
            raise AuthenticationError(f"Token refresh failed: {str(e)}")

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token (without verification for client-side use)"""
        try:
            # Note: In production, you should verify the token signature
            # For client SDK, we trust the token from the server
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

    def get_tenant_from_token(self) -> Optional[str]:
        """Extract tenant ID from current access token"""
        if not self.access_token:
            return None

        try:
            payload = self.decode_token(self.access_token)
            return payload.get('tenant_id')
        except AuthenticationError:
            return None

    def get_user_from_token(self) -> Optional[str]:
        """Extract user ID from current access token"""
        if not self.access_token:
            return None

        try:
            payload = self.decode_token(self.access_token)
            return payload.get('sub')  # Standard JWT subject claim
        except AuthenticationError:
            return None