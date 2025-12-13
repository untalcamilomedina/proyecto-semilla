from __future__ import annotations

from django import forms
from django.core.validators import validate_email

from multitenant.models import validate_subdomain


MODULE_CHOICES = [
    ("cms", "CMS (Wagtail)"),
    ("lms", "LMS (Courses)"),
    ("community", "Community"),
    ("mcp", "MCP Server"),
]


class StartOnboardingForm(forms.Form):
    org_name = forms.CharField(max_length=150)
    subdomain = forms.CharField(max_length=63, help_text="Lowercase subdomain for your tenant.")
    admin_email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_subdomain(self):
        value = self.cleaned_data["subdomain"].lower().strip()
        validate_subdomain(value)
        return value

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned


class ModulesForm(forms.Form):
    modules = forms.MultipleChoiceField(
        choices=MODULE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple
    )


class StripeConnectForm(forms.Form):
    stripe_connected = forms.BooleanField(
        required=False, initial=False, label="Stripe connected"
    )


class CustomDomainForm(forms.Form):
    custom_domain = forms.CharField(
        required=False,
        help_text="Optional custom domain (e.g., app.example.com). Leave blank to keep default.",
    )


class InviteMembersForm(forms.Form):
    emails = forms.CharField(
        required=False,
        widget=forms.Textarea,
        help_text="One email per line.",
    )

    def clean_emails(self):
        raw = self.cleaned_data["emails"]
        if not raw:
            return []
        emails: list[str] = []
        for line in raw.splitlines():
            email = line.strip()
            if not email:
                continue
            validate_email(email)
            emails.append(email.lower())
        return emails

