from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from multitenant.models import Tenant, Domain
from core.models import Membership, Role
from multitenant.schema import schema_context

User = get_user_model()

class Command(BaseCommand):
    help = "Seed a demo environment with a tenant, user, and data."

    def handle(self, *args, **options):
        self.stdout.write("Starting demo seed...")

        # 1. Ensure 'demo' tenant exists
        try:
            tenant = Tenant.objects.get(slug="demo")
            self.stdout.write(f"Tenant 'demo' already exists.")
        except Tenant.DoesNotExist:
            self.stdout.write("Creating 'demo' tenant...")
            call_command("create_tenant", "Demo Corp", "demo", plan="premium")
            tenant = Tenant.objects.get(slug="demo")

        # 2. Seed RBAC and Billing (globally)
        # Note: seed_rbac iterates all tenants, so it will cover 'demo'.
        self.stdout.write("Seeding RBAC...")
        call_command("seed_rbac")
        
        self.stdout.write("Seeding Billing...")
        call_command("seed_billing")

        # 3. Create Demo User & Assign Membership in Tenant Schema
        with schema_context(tenant.schema_name):
            email = "admin@demo.com"
            password = "password"
            
            # Check/Create User in Tenant Schema
            # We create user here so it exists in 'demo.core_user' to satisfy FK from Membership
            if not User.objects.filter(email=email).exists():
                self.stdout.write(f"Creating user {email} in schema {tenant.schema_name}...")
                user = User.objects.create_user(username=email, email=email, password=password)
            else:
                user = User.objects.get(email=email)
                self.stdout.write(f"User {email} already exists in schema {tenant.schema_name}.")

            # 4. Assign Membership
            try:
                owner_role = Role.objects.get(slug="owner")
                
                # Check existance
                if not Membership.objects.filter(user=user, organization=tenant).exists():
                     Membership.objects.create(user=user, organization=tenant, role=owner_role)
                     self.stdout.write(f"Assigned {email} as Owner of {tenant.name}")
                else:
                     self.stdout.write(f"User {email} is already a member.")
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR("Owner role not found! Run seed_rbac first."))

        self.stdout.write(self.style.SUCCESS("Seed demo completed successfully."))
