"""Viewsets del módulo CRM.

Seguridad: lectura para cualquier miembro del tenant; escritura exige el
permiso `crm.manage_crm` (PolicyPermission ya valida la membresía base).
Todos los querysets se scopean por `request.tenant`.
"""

from __future__ import annotations

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from common.api.permissions import PolicyPermission
from common.api.tenancy import request_tenant

from .models import Activity, Company, Contact, Deal
from .serializers import (
    ActivitySerializer,
    CompanySerializer,
    ContactSerializer,
    DealSerializer,
)

WRITE_ACTIONS = {"create", "update", "partial_update", "destroy"}


class CrmViewSet(viewsets.ModelViewSet):
    """Base CRM: membresía para leer, crm.manage_crm para escribir."""

    permission_classes = [PolicyPermission]

    def get_permissions(self):
        permission_classes = super().get_permissions()
        if self.action in WRITE_ACTIONS:
            self.permission_codenames = ["crm.manage_crm"]
        else:
            self.permission_codenames = []
        return permission_classes

    def get_organization(self):
        organization = request_tenant(self.request)
        if organization is None:
            raise NotFound("Tenant required.")
        return organization

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())


class CompanyViewSet(CrmViewSet):
    serializer_class = CompanySerializer
    search_fields = ["name", "domain", "industry"]
    filterset_fields = ["industry", "owner"]

    def get_queryset(self):
        return (
            Company.objects.filter(organization=self.get_organization())
            .select_related("owner")
            .annotate(contacts_count=Count("contacts"))
        )


class ContactViewSet(CrmViewSet):
    serializer_class = ContactSerializer
    search_fields = ["first_name", "last_name", "email", "phone"]
    filterset_fields = ["status", "company", "owner"]

    def get_queryset(self):
        return Contact.objects.filter(organization=self.get_organization()).select_related(
            "company", "owner"
        )


class DealViewSet(CrmViewSet):
    serializer_class = DealSerializer
    search_fields = ["name"]
    filterset_fields = ["stage", "company", "contact", "owner"]

    def get_queryset(self):
        return Deal.objects.filter(organization=self.get_organization()).select_related(
            "company", "contact", "owner"
        )

    def perform_update(self, serializer):
        # Cierra el deal automáticamente al pasar a won/lost.
        stage = serializer.validated_data.get("stage")
        if stage in {Deal.Stage.WON, Deal.Stage.LOST} and not serializer.instance.closed_at:
            serializer.save(closed_at=timezone.now())
        else:
            serializer.save()

    @action(detail=False, methods=["get"])
    def pipeline(self, request):
        """Resumen del pipeline: conteo y monto por etapa."""
        rows = (
            self.get_queryset()
            .values("stage")
            .annotate(count=Count("id"), total_amount=Sum("amount"))
            .order_by("stage")
        )
        summary = {
            row["stage"]: {
                "count": row["count"],
                "total_amount": str(row["total_amount"] or "0.00"),
            }
            for row in rows
        }
        return Response({"stages": summary})


class ActivityViewSet(CrmViewSet):
    serializer_class = ActivitySerializer
    search_fields = ["subject", "content"]
    filterset_fields = ["kind", "contact", "company", "deal"]

    def get_queryset(self):
        return Activity.objects.filter(organization=self.get_organization()).select_related(
            "contact", "company", "deal", "created_by"
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization(), created_by=self.request.user)
