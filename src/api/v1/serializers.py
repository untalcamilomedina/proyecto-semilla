from __future__ import annotations

from rest_framework import serializers

from api.models import ApiKey
from billing.models import Invoice, Plan, Subscription
from core.models import Membership, Permission, Role
from multitenant.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "slug", "schema_name", "plan_code", "enabled_modules"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "module", "codename", "name", "description", "is_system"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        slug_field="codename", queryset=Permission.objects.all(), many=True, required=False
    )

    class Meta:
        model = Role
        fields = ["id", "name", "slug", "description", "position", "is_system", "permissions"]
        read_only_fields = ["is_system", "slug"]


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    role_slug = serializers.SlugRelatedField(
        source="role", slug_field="slug", queryset=Role.objects.all()
    )

    class Meta:
        model = Membership
        fields = ["id", "user", "user_email", "role_slug", "is_active", "joined_at"]
        read_only_fields = ["joined_at"]


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["id", "code", "name", "description", "seat_limit", "trial_days", "roles_on_activation"]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "status",
            "quantity",
            "cancel_at_period_end",
            "current_period_end",
            "trial_end",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "stripe_invoice_id",
            "status",
            "amount_paid",
            "currency",
            "hosted_invoice_url",
            "invoice_pdf",
            "created_at",
        ]


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ["id", "name", "prefix", "scopes", "revoked_at", "last_used_at", "created_at"]
        read_only_fields = ["prefix", "revoked_at", "last_used_at", "created_at"]


class ApiKeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    scopes = serializers.ListField(child=serializers.CharField(), required=False)

