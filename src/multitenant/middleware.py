from __future__ import annotations

from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.utils.deprecation import MiddlewareMixin

from .models import Domain, Tenant
from .schema import PUBLIC_SCHEMA_NAME, schema_context, set_schema


class TenantMiddleware(MiddlewareMixin):
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
        except (OperationalError, ProgrammingError):
            tenant_public = None

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
        else:
            set_schema(PUBLIC_SCHEMA_NAME)
            request.tenant = None

    def process_response(self, request, response):
        if getattr(settings, "MULTITENANT_MODE", "off") == "schema":
            set_schema(PUBLIC_SCHEMA_NAME)
        return response
