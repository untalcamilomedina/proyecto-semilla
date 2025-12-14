from __future__ import annotations

from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import ApiKey
from api.permissions import PolicyPermission
from billing.models import Invoice, Plan, Subscription
from core.models import Membership, Permission, Role
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
)


class TenantViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [PolicyPermission]
    serializer_class = TenantSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.tenant)
        return Response(serializer.data)


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
    permission_codenames = ["core.invite_members"]

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


def request_tenant(request):
    return getattr(request, "tenant", None)
