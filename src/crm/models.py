"""Modelos del módulo CRM (opcional, flag ENABLE_CRM).

CRM ligero multitenant: empresas, contactos, oportunidades (pipeline) y
actividades. Todos los modelos se scopean por `organization` y el API exige
membresía (lectura) + `crm.manage_crm` (escritura).
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models


class Company(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="crm_companies"
    )
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200, blank=True, default="")
    industry = models.CharField(max_length=120, blank=True, default="")
    size = models.CharField(max_length=50, blank=True, default="")
    website = models.URLField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_companies",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("organization", "name")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.organization.slug}:{self.name}"


class Contact(models.Model):
    class Status(models.TextChoices):
        LEAD = "lead", "Lead"
        PROSPECT = "prospect", "Prospect"
        CUSTOMER = "customer", "Customer"
        INACTIVE = "inactive", "Inactive"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="crm_contacts"
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts"
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    position = models.CharField(max_length=120, blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEAD)
    source = models.CharField(max_length=120, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_contacts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "email"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.first_name} {self.last_name}".strip()


class Deal(models.Model):
    class Stage(models.TextChoices):
        NEW = "new", "New"
        QUALIFIED = "qualified", "Qualified"
        PROPOSAL = "proposal", "Proposal"
        NEGOTIATION = "negotiation", "Negotiation"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="crm_deals"
    )
    name = models.CharField(max_length=200)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="usd")
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.NEW)
    probability = models.PositiveSmallIntegerField(default=0, help_text="0-100 (%)")
    expected_close_date = models.DateField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_deals",
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "stage"])]

    @property
    def is_open(self) -> bool:
        return self.stage not in {self.Stage.WON, self.Stage.LOST}

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.organization.slug}:{self.name} [{self.stage}]"


class Activity(models.Model):
    class Kind(models.TextChoices):
        NOTE = "note", "Note"
        CALL = "call", "Call"
        EMAIL = "email", "Email"
        MEETING = "meeting", "Meeting"
        TASK = "task", "Task"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="crm_activities"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.NOTE)
    subject = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True, related_name="activities"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True, related_name="activities"
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.CASCADE, null=True, blank=True, related_name="activities"
    )
    due_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_activities",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "activities"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.kind}: {self.subject}"
