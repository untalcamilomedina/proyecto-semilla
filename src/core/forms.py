from __future__ import annotations

import json

from django import forms

from .models import Permission, Role


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "description", "position"]


class RolePermissionsForm(forms.Form):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all().order_by("module", "codename"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )


class RoleImportForm(forms.Form):
    json_data = forms.CharField(widget=forms.Textarea, help_text="Paste exported role JSON.")

    def clean_json_data(self):
        raw = self.cleaned_data["json_data"]
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("Invalid JSON.") from exc

