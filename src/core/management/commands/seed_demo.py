from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from multitenant.models import Tenant, Domain
from core.models import Membership, Role
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context

User = get_user_model()


class Command(BaseCommand):
    help = "Seed a demo environment with a tenant, user, and data."

    def handle(self, *args, **options):
        self.stdout.write("Starting demo seed...")

        with schema_context(PUBLIC_SCHEMA_NAME):
            try:
                tenant = Tenant.objects.get(slug="demo")
                self.stdout.write("Tenant 'demo' already exists.")
            except Tenant.DoesNotExist:
                self.stdout.write("Creating 'demo' tenant...")
                call_command("create_tenant", "Demo Corp", "demo", plan="premium")
                tenant = Tenant.objects.get(slug="demo")

            Domain.objects.get_or_create(
                domain="localhost",
                defaults={"tenant": tenant, "is_primary": False},
            )
            Domain.objects.get_or_create(
                domain="127.0.0.1",
                defaults={"tenant": tenant, "is_primary": False},
            )

        self.stdout.write("Seeding RBAC...")
        call_command("seed_rbac")

        self.stdout.write("Seeding Billing...")
        call_command("seed_billing")

        with schema_context(tenant.schema_name):
            tenant_local = Tenant.objects.get(id=tenant.id)
            email = "admin@demo.com"
            password = "password"

            if not User.objects.filter(email=email).exists():
                self.stdout.write(f"Creating user {email} in schema {tenant.schema_name}...")
                user = User.objects.create_user(username=email, email=email, password=password)
            else:
                user = User.objects.get(email=email)
                self.stdout.write(f"User {email} already exists in schema {tenant.schema_name}.")

            email_address, _created = EmailAddress.objects.get_or_create(
                user=user,
                email=email,
                defaults={"verified": True, "primary": True},
            )
            if not email_address.verified or not email_address.primary:
                email_address.verified = True
                email_address.primary = True
                email_address.save(update_fields=["verified", "primary"])

            try:
                owner_role = Role.objects.get(organization=tenant_local, slug="owner")

                membership, created = Membership.objects.get_or_create(
                    user=user,
                    organization=tenant_local,
                    defaults={"role": owner_role},
                )
                if created:
                    self.stdout.write(f"Assigned {email} as Owner of {tenant_local.name}")
                else:
                    membership.role = owner_role
                    membership.save(update_fields=["role"])
                    self.stdout.write(f"User {email} is already a member.")
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR("Owner role not found! Run seed_rbac first."))

        self.stdout.write(self.style.SUCCESS("Seed demo completed successfully."))
