from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.conf import settings
from .adapters import get_provider
from integrations.models import IntegrationConnection

class OAuthConnectView(APIView):
    """
    Initiates the OAuth Flow.
    GET /api/v1/integrations/{provider}/connect
    """
    def get(self, request, provider_name):
        try:
            adapter = get_provider(provider_name)
        except ValueError:
            return Response({"error": "Invalid provider"}, status=400)
            
        # State should ideally be random + saved in session/cache to prevent CSRF
        # For MVP, we pass a simple state or user_id signature
        state = f"user_{request.user.id}" 
        
        auth_url = adapter.get_authorization_url(state=state)
        
        # Return the URL so the frontend can redirect (API-First style)
        return Response({"auth_url": auth_url})

class OAuthCallbackView(APIView):
    """
    Handles the provider callback.
    GET /api/v1/integrations/{provider}/callback?code=...
    """
    def get(self, request, provider_name):
        code = request.query_params.get("code")
        error = request.query_params.get("error")
        
        if error:
            return Response({"error": error}, status=400)
        
        if not code:
            return Response({"error": "No code provided"}, status=400)
            
        try:
            adapter = get_provider(provider_name)
            
            # Exchange code for tokens
            # This is async in our adapter, but DRF Views are sync by default unless using adrf or async_to_sync
            # We used 'async def' in adapters. Integration needs `asgiref`.
            from asgiref.sync import async_to_sync
            token_data = async_to_sync(adapter.exchange_code)(code)
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in") # Optional handling
            
            # Save Encrypted
            IntegrationConnection.objects.update_or_create(
                user=request.user,
                provider=provider_name,
                defaults={
                    "access_token_enc": "", # Will be set by set_token
                    # We need to set them via the helper method to encrypt
                }
            )
            
            # Re-fetch to use model methods for encryption (cleaner)
            conn, _ = IntegrationConnection.objects.get_or_create(
                user=request.user, 
                provider=provider_name
            )
            conn.set_token(access_token, refresh_token)
            conn.save()
            
            # Redirect to Frontend Success Page
            frontend_success = f"{settings.FRONTEND_URL}/integrations?status=success&provider={provider_name}"
            return redirect(frontend_success)
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)
