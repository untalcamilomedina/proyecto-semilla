from __future__ import annotations

from django.core.management.base import BaseCommand

from core.services.seed import seed_default_roles, seed_system_permissions
from multitenant.models import Tenant


from multitenant.schema import schema_context

class Command(BaseCommand):
    help = "Seed system permissions and default roles for all tenants."

    def handle(self, *args, **options):
        seed_system_permissions()
        # Iterate over all tenants
        for tenant in Tenant.objects.all():
            # Switch to the tenant's schema
            with schema_context(tenant.schema_name):
                seed_default_roles(tenant)
                self.stdout.write(self.style.SUCCESS(f"Seeded roles for {tenant.slug}"))

