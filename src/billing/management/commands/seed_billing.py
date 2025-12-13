from __future__ import annotations

from django.core.management.base import BaseCommand

from billing.services.seed import seed_demo_plans
from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


class Command(BaseCommand):
    help = "Seed demo plans/prices for all tenants."

    def handle(self, *args, **options):
        with schema_context(PUBLIC_SCHEMA_NAME):
            tenants = list(Tenant.objects.all())

        for tenant_public in tenants:
            with schema_context(tenant_public.schema_name):
                try:
                    tenant_local = Tenant.objects.get(id=tenant_public.id)
                except Tenant.DoesNotExist:
                    continue
                seed_demo_plans(tenant_local)
                self.stdout.write(self.style.SUCCESS(f"Seeded billing for {tenant_local.slug}"))

