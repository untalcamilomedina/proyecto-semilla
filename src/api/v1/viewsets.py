from __future__ import annotations

from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import ApiKey
from api.permissions import PolicyPermission
from billing.models import Invoice, Plan, Subscription
from common.api.tenancy import request_tenant
from core.models import ActivityLog, Membership, Permission, Role
from core.services.members import invite_members_to_org

from .serializers import (
    ActivityLogSerializer,
    ApiKeyCreateSerializer,
    ApiKeySerializer,
    InvoiceSerializer,
    MembershipInviteSerializer,
    MembershipSerializer,
    PasswordChangeSerializer,
    PermissionSerializer,
    PlanSerializer,
    RoleSerializer,
    SubscriptionSerializer,
    TenantSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        """Get current user profile."""
        serializer = self.get_serializer(self.get_object())
        return Response({"is_authenticated": True, "user": serializer.data})

    def partial_update(self, request, *args, **kwargs):
        """Update current user profile."""
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(instance).data)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Change current user password."""
        instance = self.get_object()
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not instance.check_password(serializer.validated_data["current_password"]):
            return Response(
                {"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST
            )

        instance.set_password(serializer.validated_data["new_password"])
        instance.save()
        return Response({"detail": "Password updated successfully."})


class TenantViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [PolicyPermission]
    serializer_class = TenantSerializer

    def get_object(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            from rest_framework.exceptions import NotFound

            raise NotFound("No tenant context available.")
        return tenant

    def retrieve(self, request, *args, **kwargs):
        """Get current tenant details."""
        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            self.permission_codename = "core.manage_organization"
        return super().get_permissions()


class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [PolicyPermission]


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [PolicyPermission]
    permission_codename = "core.manage_roles"

    def get_queryset(self):
        return Role.objects.filter(organization=request_tenant(self.request)).prefetch_related(
            "permissions"
        )

    def perform_create(self, serializer):
        serializer.save(organization=request_tenant(self.request))


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [PolicyPermission]

    def get_permissions(self):
        permission_classes = super().get_permissions()
        if self.action == "invite":
            # Assign explicitly to the instance for PolicyPermission to pick up
            self.permission_codenames = ["core.invite_members"]
        elif self.action in ["update", "partial_update", "destroy"]:
            self.permission_codenames = ["core.manage_roles"]
        else:
            # list, retrieve: solo exige membresía (la valida PolicyPermission)
            self.permission_codenames = []
        return permission_classes

    def get_queryset(self):
        return Membership.objects.filter(organization=request_tenant(self.request)).select_related(
            "role", "user"
        )

    def perform_create(self, serializer):
        serializer.save(organization=request_tenant(self.request))

    @action(detail=False, methods=["post"])
    def invite(self, request, *args, **kwargs):
        serializer = MembershipInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invited = invite_members_to_org(
            request_tenant(request),
            serializer.validated_data["emails"],
            role_slug=serializer.validated_data.get("role_slug") or "member",
            inviter=request.user,
        )
        return Response({"invited": invited}, status=status.HTTP_200_OK)


class PlanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PlanSerializer
    permission_classes = [PolicyPermission]

    def get_queryset(self):
        return Plan.objects.filter(
            organization=request_tenant(self.request), is_active=True, is_public=True
        ).prefetch_related("prices")


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [PolicyPermission]
    permission_codename = "billing.manage_billing"

    def get_queryset(self):
        return Subscription.objects.filter(
            organization=request_tenant(self.request)
        ).select_related("plan")

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Suscripción activa (o más reciente) del tenant actual."""
        subscription = self.get_queryset().order_by("-created_at").first()
        if subscription is None:
            return Response({"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND)
        data = SubscriptionSerializer(subscription).data
        data["usage"] = {
            "items_used": subscription.items_used,
            "max_items": subscription.plan.max_items,
            "requests_used": subscription.requests_used,
            "max_requests": subscription.plan.max_requests,
        }
        return Response(data)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Crea una sesión de Stripe Checkout para un price del tenant.

        Body: {"price_id": int, "success_url": str?, "cancel_url": str?}
        """
        from django.conf import settings as dj_settings

        from billing.models import Price
        from billing.services.stripe import StripeError, create_checkout_session

        tenant = request_tenant(request)
        price_id = request.data.get("price_id")
        if not price_id:
            return Response(
                {"price_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            price = Price.objects.select_related("plan").get(
                id=price_id, plan__organization=tenant, is_active=True
            )
        except Price.DoesNotExist:
            return Response({"price_id": ["Invalid price."]}, status=status.HTTP_400_BAD_REQUEST)

        frontend = dj_settings.FRONTEND_URL.rstrip("/")
        success_url = request.data.get("success_url") or f"{frontend}/billing?status=success"
        cancel_url = request.data.get("cancel_url") or f"{frontend}/billing?status=cancelled"
        # Solo permitimos redirecciones al propio frontend configurado.
        if not (success_url.startswith(frontend) and cancel_url.startswith(frontend)):
            return Response(
                {"detail": "Redirect URLs must point to the configured FRONTEND_URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = create_checkout_session(
                organization=tenant,
                price=price,
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"session_id": result.session_id, "url": result.url})

    @action(detail=False, methods=["post"])
    def portal(self, request):
        """Crea una sesión del Billing Portal de Stripe."""
        from django.conf import settings as dj_settings

        from billing.services.stripe import StripeError, create_billing_portal_session

        frontend = dj_settings.FRONTEND_URL.rstrip("/")
        return_url = request.data.get("return_url") or f"{frontend}/billing"
        if not return_url.startswith(frontend):
            return Response(
                {"detail": "Redirect URLs must point to the configured FRONTEND_URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            url = create_billing_portal_session(
                organization=request_tenant(request), return_url=return_url
            )
        except StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"url": url})


class InvoiceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [PolicyPermission]
    permission_codename = "billing.manage_billing"

    def get_queryset(self):
        return Invoice.objects.filter(organization=request_tenant(self.request))


class ApiKeyViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ApiKeySerializer
    permission_classes = [PolicyPermission]
    permission_codename = "core.manage_roles"

    def get_queryset(self):
        return ApiKey.objects.filter(
            organization=request_tenant(self.request), revoked_at__isnull=True
        )

    def create(self, request, *args, **kwargs):
        serializer = ApiKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, plain = ApiKey.generate(
            organization=request_tenant(request),
            user=request.user,
            name=serializer.validated_data["name"],
            scopes=serializer.validated_data.get("scopes") or [],
        )
        output = ApiKeySerializer(obj).data
        output["key"] = plain
        return Response(output, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        key = self.get_object()
        key.revoked_at = timezone.now()
        key.save(update_fields=["revoked_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivityLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [PolicyPermission]
    permission_codename = "core.view_audit_logs"

    def get_queryset(self):
        return ActivityLog.objects.filter(organization=request_tenant(self.request)).select_related(
            "actor"
        )
