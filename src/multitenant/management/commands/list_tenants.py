from __future__ import annotations

from django.core.management.base import BaseCommand

from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


class Command(BaseCommand):
    help = "List all tenants and their domains."

    def handle(self, *args, **options):
        with schema_context(PUBLIC_SCHEMA_NAME):
            for tenant in Tenant.objects.all().order_by("slug"):
                domains = ", ".join(tenant.domains.values_list("domain", flat=True))
                self.stdout.write(f"{tenant.slug}\t{tenant.schema_name}\t{domains}")
