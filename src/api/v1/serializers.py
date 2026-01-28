from __future__ import annotations

from rest_framework import serializers

from api.models import ApiKey
from billing.models import Invoice, Plan, Subscription
from core.models import User, Membership, Permission, Role, ActivityLog
from multitenant.models import Tenant


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "is_active"]
        read_only_fields = ["id", "email", "username", "is_active"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "New passwords must match."})
        return data


class TenantSerializer(serializers.ModelSerializer):
    domain_base = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "slug",
            "schema_name",
            "plan_code",
            "enabled_modules",
            "branding",
            "domain_base",
        ]
        read_only_fields = ["id", "slug", "schema_name", "plan_code", "domain_base"]

    def get_domain_base(self, _obj: Tenant) -> str:
        from django.conf import settings

        return getattr(settings, "DOMAIN_BASE", "notionapps.dev")


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
    role_name = serializers.CharField(source="role.name", read_only=True)
    role_slug = serializers.SlugRelatedField(
        source="role", slug_field="slug", queryset=Role.objects.all()
    )

    class Meta:
        model = Membership
        fields = ["id", "user", "user_email", "role_slug", "role_name", "is_active", "joined_at"]
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


class MembershipInviteSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(), allow_empty=False)
    role_slug = serializers.SlugField(required=False)


class ActivityLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = ActivityLog
        fields = ["id", "actor_email", "action", "object_repr", "description", "created_at"]
