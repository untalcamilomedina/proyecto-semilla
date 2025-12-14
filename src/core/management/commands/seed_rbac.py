from __future__ import annotations

from django.core.management.base import BaseCommand

from core.services.seed import seed_default_roles, seed_system_permissions
from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


class Command(BaseCommand):
    help = "Seed system permissions and default roles for all tenants."

    def handle(self, *args, **options):
        with schema_context(PUBLIC_SCHEMA_NAME):
            seed_system_permissions()
            tenants = list(Tenant.objects.all())

        for tenant_public in tenants:
            with schema_context(tenant_public.schema_name):
                try:
                    tenant_local = Tenant.objects.get(id=tenant_public.id)
                except Tenant.DoesNotExist:
                    continue
                seed_default_roles(tenant_local)
                self.stdout.write(self.style.SUCCESS(f"Seeded roles for {tenant_local.slug}"))
