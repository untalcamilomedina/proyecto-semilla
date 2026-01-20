from __future__ import annotations

from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import ApiKey
from api.permissions import PolicyPermission
from billing.models import Invoice, Plan, Subscription
from core.models import Membership, Permission, Role, ActivityLog
from core.services.members import invite_members_to_org

from .serializers import (
    ApiKeyCreateSerializer,
    ApiKeySerializer,
    InvoiceSerializer,
    MembershipSerializer,
    MembershipInviteSerializer,
    PermissionSerializer,
    PlanSerializer,
    RoleSerializer,
    SubscriptionSerializer,
    TenantSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    ActivityLogSerializer,
)


class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        """Get current user profile."""
        serializer = self.get_serializer(self.get_object())
        return Response({
            "is_authenticated": True,
            "user": serializer.data
        })

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
            return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        instance.set_password(serializer.validated_data["new_password"])
        instance.save()
        return Response({"detail": "Password updated successfully."})


class TenantViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [PolicyPermission]
    serializer_class = TenantSerializer

    def get_object(self):
        return self.request.tenant

    def retrieve(self, request, *args, **kwargs):
        """Get current tenant details."""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Update current tenant settings."""
        self.permission_codename = "core.manage_organization" # Requiere permiso para editar
        return super().partial_update(request, *args, **kwargs)


class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [PolicyPermission]


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [PolicyPermission]
    permission_codename = "core.manage_roles"

    def get_queryset(self):
        return Role.objects.filter(organization=request_tenant(self.request)).prefetch_related("permissions")

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
            # list, retrieve: No specific codename required, just membership (handled by PolicyPermission base check)
            self.permission_codenames = []
        return permission_classes

    def get_queryset(self):
        return Membership.objects.filter(organization=request_tenant(self.request)).select_related("role", "user")

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
        return Plan.objects.filter(organization=request_tenant(self.request), is_active=True, is_public=True)


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [PolicyPermission]
    permission_codename = "billing.manage_billing"

    def get_queryset(self):
        return Subscription.objects.filter(organization=request_tenant(self.request)).select_related("plan")


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
        return ApiKey.objects.filter(organization=request_tenant(self.request), revoked_at__isnull=True)

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
        return ActivityLog.objects.filter(organization=request_tenant(self.request)).select_related("actor")


def request_tenant(request):
    return getattr(request, "tenant", None)
