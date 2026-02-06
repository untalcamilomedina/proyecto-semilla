from __future__ import annotations

import logging
import secrets

from asgiref.sync import async_to_sync
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.models import IntegrationConnection

from .adapters import get_provider

logger = logging.getLogger(__name__)


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

        # Cryptographically secure state to prevent OAuth CSRF
        state = secrets.token_urlsafe(32)
        request.session[f"oauth_state_{provider_name}"] = state
        request.session.save()

        auth_url = adapter.get_authorization_url(state=state)

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
            return Response({"error": "No authorization code provided."}, status=400)

        # Validate OAuth state to prevent CSRF
        received_state = request.query_params.get("state")
        expected_state = request.session.pop(f"oauth_state_{provider_name}", None)

        if not received_state or not expected_state or received_state != expected_state:
            logger.warning(
                "OAuth state mismatch for provider=%s user=%s",
                provider_name,
                request.user.id,
            )
            return Response(
                {"error": "Invalid OAuth state. Please initiate the connection again."},
                status=400,
            )

        try:
            adapter = get_provider(provider_name)

            token_data = async_to_sync(adapter.exchange_code)(code)

            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")

            if not access_token:
                return Response(
                    {"error": "No access token received from provider."},
                    status=502,
                )

            conn, _ = IntegrationConnection.objects.update_or_create(
                user=request.user,
                provider=provider_name,
                defaults={"access_token_enc": "", "refresh_token_enc": ""},
            )
            conn.set_token(access_token, refresh_token)
            conn.save()

            frontend_success = (
                f"{settings.FRONTEND_URL}/integrations"
                f"?status=success&provider={provider_name}"
            )
            return redirect(frontend_success)

        except ValueError as e:
            logger.exception("OAuth value error for provider=%s", provider_name)
            return Response({"error": "Invalid provider configuration."}, status=400)
        except Exception:
            logger.exception("OAuth callback failed for provider=%s", provider_name)
            return Response(
                {"error": "Failed to complete OAuth connection. Please try again."},
                status=500,
            )
