from __future__ import annotations

from django.core.validators import validate_email as django_validate_email
from rest_framework import serializers

from multitenant.models import validate_subdomain


class StartOnboardingSerializer(serializers.Serializer):
    org_name = serializers.CharField(max_length=150)
    subdomain = serializers.CharField(max_length=63)
    admin_email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate_subdomain(self, value):
        value = value.lower().strip()
        validate_subdomain(value)
        return value

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data


class ModulesSerializer(serializers.Serializer):
    MODULE_CHOICES = [
        ("cms", "CMS (Wagtail)"),
        ("lms", "LMS (Courses)"),
        ("community", "Community"),
        ("mcp", "MCP Server"),
    ]
    modules = serializers.MultipleChoiceField(choices=MODULE_CHOICES, required=False)


class StripeConnectSerializer(serializers.Serializer):
    stripe_connected = serializers.BooleanField(required=False, default=False)


class CustomDomainSerializer(serializers.Serializer):
    custom_domain = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class InviteMembersSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(), required=False, allow_empty=True
    )

    def to_internal_value(self, data):
        # Allow sending a string of emails separated by newlines or commas
        if isinstance(data, dict) and "emails" in data and isinstance(data["emails"], str):
            raw = data["emails"]
            emails = []
            for line in raw.replace(",", "\n").splitlines():
                email = line.strip()
                if email:
                    emails.append(email)
            data = data.copy()
            data["emails"] = emails
        return super().to_internal_value(data)
