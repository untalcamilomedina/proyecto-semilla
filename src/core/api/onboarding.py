from __future__ import annotations

from django.contrib.auth import login
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import OnboardingState
from core.services.onboarding import (
    invite_members,
    mark_stripe_connected,
    set_custom_domain,
    set_modules,
    start_onboarding,
)
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context

from .serializers import (
    CustomDomainSerializer,
    InviteMembersSerializer,
    ModulesSerializer,
    StartOnboardingSerializer,
    StripeConnectSerializer,
)


class OnboardingViewSet(viewsets.ViewSet):
    """
    API ViewSet for managing the onboarding flow.
    Replaces the legacy Django Template views.
    """

    def get_permissions(self):
        if self.action == "start":
            return [AllowAny()]
        return [IsAuthenticated()]

    def _get_state(self, request) -> OnboardingState:
        # User should be authenticated and owner of the tenant
        # We find the OnboardingState related to the user's primary tenant (or via some link)
        # For simplicity in this flow, we assume the user just created the tenant in step 1
        # and is logged in. We look up state by the tenant they belong to or email.
        # But OnboardingState is in 'public' schema.
        
        user_email = request.user.email
        with schema_context(PUBLIC_SCHEMA_NAME):
            # Find in-progress state for this user's email
            state = OnboardingState.objects.filter(
                owner_email=user_email, is_complete=False
            ).first()
            if not state:
                # Fallback: maybe completed?
                state = OnboardingState.objects.filter(owner_email=user_email).order_by("-created_at").first()
            
            return state

    @action(detail=False, methods=["post"])
    def start(self, request):
        serializer = StartOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            # Check if user is authenticated (post-signup flow)
            source_user = request.user if request.user.is_authenticated else None
            
            result = start_onboarding(
                org_name=data["org_name"],
                subdomain=data["subdomain"],
                admin_email=data.get("admin_email"),
                password=data.get("password"),
                language=data.get("language", "es"),
                stripe_connected=data.get("stripe_connected", False),
                stripe_public_key=data.get("stripe_public_key", ""),
                stripe_secret_key=data.get("stripe_secret_key", ""),
                stripe_webhook_secret=data.get("stripe_webhook_secret", ""),
                source_user=source_user,
            )
            
            # Log the user in immediately so they can proceed to next steps
            # Pass backend='django.contrib.auth.backends.ModelBackend' if needed
            # We need to find the user object created in the tenant schema
            # But 'login' requires the user object.
            # start_onboarding creates the user in the tenant schema.
            # Authentication in this system might be complex with schemas.
            # However, standard login helper needs a user object.
            # Let's rely on the frontend to login using the credentials, 
            # OR we can return the user info and token if using token auth.
            
            return Response(
                {
                    "detail": "Organization created successfully",
                    "tenant_id": result.tenant.id,
                    "state_id": result.state.id,
                    "next_step": 2,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            # Handle specific business logic errors (e.g. subdomain taken)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"])
    def status(self, request):
        state = self._get_state(request)
        if not state:
            return Response(
                {"detail": "No active onboarding found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            "current_step": state.current_step,
            "completed_steps": state.completed_steps,
            "is_complete": state.is_complete,
            "data": state.data,
            "tenant_slug": state.tenant.slug,
        })

    @action(detail=False, methods=["post"])
    def modules(self, request):
        state = self._get_state(request)
        if not state:
            return Response({"detail": "State not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ModulesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # MultipleChoiceField in DRF returns a set, ensuring it's a list for JSONField
        modules = list(serializer.validated_data.get("modules", []))
        set_modules(state, modules)
        return Response({"detail": "Modules updated", "next_step": 3})

    @action(detail=False, methods=["post"])
    def stripe(self, request):
        state = self._get_state(request)
        if not state:
            return Response({"detail": "State not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StripeConnectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        mark_stripe_connected(state, serializer.validated_data.get("stripe_connected", False))
        return Response({"detail": "Stripe configured", "next_step": 4})

    @action(detail=False, methods=["post"])
    def domain(self, request):
        state = self._get_state(request)
        if not state:
            return Response({"detail": "State not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomDomainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        set_custom_domain(state, serializer.validated_data.get("custom_domain"))
        return Response({"detail": "Domain updated", "next_step": 5})

    @action(detail=False, methods=["post"])
    def invite(self, request):
        state = self._get_state(request)
        if not state:
            return Response({"detail": "State not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = InviteMembersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        count = invite_members(state, serializer.validated_data.get("emails", []))
        return Response({"detail": f"Invited {count} members", "next_step": 6, "is_complete": True})
