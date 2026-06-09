from __future__ import annotations

import logging

from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from common.rls import set_tenant_id

from .models import Domain, Tenant
from .schema import PUBLIC_SCHEMA_NAME, schema_context, set_schema

logger = logging.getLogger(__name__)

# Rutas que deben responder aunque la BD esté caída (probes de liveness).
_DB_OPTIONAL_PATHS = ("/healthz",)


class TenantMiddleware(MiddlewareMixin):
    """Resuelve el tenant por dominio y fija el schema de Postgres.

    Corre ANTES de AuthenticationMiddleware (el usuario aún no está
    disponible aquí): cualquier lógica que dependa de request.user debe
    vivir en permisos DRF o middlewares posteriores.
    """

    def process_request(self, request):
        if getattr(settings, "MULTITENANT_MODE", "off") != "schema":
            request.tenant = None
            return

        host = request.get_host().split(":")[0].lower()
        tenant_public = None
        try:
            with schema_context(PUBLIC_SCHEMA_NAME):
                domain = Domain.objects.select_related("tenant").get(
                    domain=host, tenant__is_active=True
                )
                tenant_public = domain.tenant
        except Domain.DoesNotExist:
            tenant_public = None
        except ProgrammingError:
            # Migraciones aún no aplicadas (instalación fresca): seguimos en
            # public para permitir healthz/migrate, pero lo dejamos registrado.
            logger.warning("TenantMiddleware: tablas de multitenancy no disponibles aún.")
            tenant_public = None
        except OperationalError:
            # BD caída: NUNCA servir silenciosamente desde el schema público.
            logger.exception("TenantMiddleware: error de conexión a la base de datos.")
            if request.path.startswith(_DB_OPTIONAL_PATHS):
                request.tenant = None
                return None
            return JsonResponse({"detail": "Service temporarily unavailable."}, status=503)

        if tenant_public:
            set_schema(tenant_public.schema_name)
            try:
                tenant_local = Tenant.objects.get(schema_name=tenant_public.schema_name)
            except Tenant.DoesNotExist:
                tenant_local = Tenant.objects.create(
                    id=tenant_public.id,
                    name=tenant_public.name,
                    slug=tenant_public.slug,
                    schema_name=tenant_public.schema_name,
                    is_active=tenant_public.is_active,
                    plan_code=tenant_public.plan_code,
                    trial_ends_at=tenant_public.trial_ends_at,
                    enabled_modules=tenant_public.enabled_modules,
                    branding=getattr(tenant_public, "branding", {}) or {},
                )
            request.tenant = tenant_local

            # RLS: Set tenant_id for Row-Level Security policies
            set_tenant_id(tenant_local.id)
        else:
            set_schema(PUBLIC_SCHEMA_NAME)
            request.tenant = None

    def process_response(self, request, response):
        if getattr(settings, "MULTITENANT_MODE", "off") == "schema":
            set_schema(PUBLIC_SCHEMA_NAME)
        return response
