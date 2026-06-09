"""Serializers del módulo CRM (campos explícitos, sin __all__)."""

from __future__ import annotations

from rest_framework import serializers

from crm.models import Activity, Company, Contact, Deal


class CompanySerializer(serializers.ModelSerializer):
    contacts_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "domain",
            "industry",
            "size",
            "website",
            "notes",
            "owner",
            "contacts_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ContactSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True, default="")

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "position",
            "status",
            "source",
            "notes",
            "company",
            "company_name",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DealSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True, default="")
    contact_name = serializers.CharField(source="contact.__str__", read_only=True, default="")

    class Meta:
        model = Deal
        fields = [
            "id",
            "name",
            "company",
            "company_name",
            "contact",
            "contact_name",
            "amount",
            "currency",
            "stage",
            "probability",
            "expected_close_date",
            "closed_at",
            "owner",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "closed_at", "created_at", "updated_at"]

    def validate_probability(self, value: int) -> int:
        if value > 100:
            raise serializers.ValidationError("Probability must be between 0 and 100.")
        return value


class ActivitySerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True, default="")

    class Meta:
        model = Activity
        fields = [
            "id",
            "kind",
            "subject",
            "content",
            "contact",
            "company",
            "deal",
            "due_at",
            "completed_at",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
