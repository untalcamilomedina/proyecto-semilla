from django.db import models
from django.conf import settings
import uuid

class Diagram(models.Model):
    """
    Core business entity representing a Diagram (Flow or ERD).
    It stores the Canonical Model in JSON format.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diagrams"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    
    # Types defined in canonical spec
    DIAGRAM_TYPE_FLOW = "flow"
    DIAGRAM_TYPE_ERD = "erd"
    
    TYPE_CHOICES = [
        (DIAGRAM_TYPE_FLOW, "Flow Diagram"),
        (DIAGRAM_TYPE_ERD, "Entity-Relationship Diagram"),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DIAGRAM_TYPE_FLOW)
    
    # Actual Canonical Data (validated by Pydantic in API layer)
    spec = models.JSONField(default=dict, help_text="Canonical JSON Spec (FlowSpec or ERDSpec)")
    
    # Metadata
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.type})"

class Job(models.Model):
    """
    Async Job tracker for long-running tasks.
    """
    STATUS_PENDING = "PENDING"
    STATUS_RUNNING = "RUNNING"
    STATUS_SUCCEEDED = "SUCCEEDED"
    STATUS_FAILED = "FAILED"
    
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCEEDED, "Succeeded"),
        (STATUS_FAILED, "Failed"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs"
    )
    type = models.CharField(max_length=50, help_text="Job type identifier (e.g. 'scan_notion')")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    progress = models.FloatField(default=0.0, help_text="0.0 to 1.0")
    
    result = models.JSONField(default=dict, blank=True)
    error = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Job {self.id} [{self.status}]"

# --- Security & OAuth Models (Phase 6 & 7) ---

import os

from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured


def get_cipher_suite():
    """Use a dedicated encryption key, independent of SECRET_KEY."""
    encryption_key = os.environ.get("FIELD_ENCRYPTION_KEY")
    if not encryption_key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY must be set. "
            "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    return Fernet(encryption_key.encode())

class EncryptedTextField(models.TextField):
    """
    Custom field that encrypts data on save and decrypts on access is tricky 
    without a heavy library.
    For simplicity/transparency, we'll store as Text and use model methods.
    """
    pass

class IntegrationConnection(models.Model):
    """
    Stores OAuth tokens for external tools (Notion, Miro).
    Tokens are ENCRYPTED at rest.
    """
    PROVIDER_NOTION = "notion"
    PROVIDER_MIRO = "miro"
    
    PROVIDER_CHOICES = [
        (PROVIDER_NOTION, "Notion"),
        (PROVIDER_MIRO, "Miro"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="connections")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    
    # Encrypted Data
    access_token_enc = models.TextField(help_text="Encrypted Access Token")
    refresh_token_enc = models.TextField(blank=True, null=True, help_text="Encrypted Refresh Token")
    
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ["user", "provider"]
        
    def set_token(self, token: str, refresh: str = None):
        cipher = get_cipher_suite()
        self.access_token_enc = cipher.encrypt(token.encode()).decode()
        if refresh:
            self.refresh_token_enc = cipher.encrypt(refresh.encode()).decode()
            
    def get_token(self) -> str:
        cipher = get_cipher_suite()
        return cipher.decrypt(self.access_token_enc.encode()).decode()
    
    def get_refresh_token(self) -> str:
        if not self.refresh_token_enc:
            return None
        cipher = get_cipher_suite()
        return cipher.decrypt(self.refresh_token_enc.encode()).decode()

class UserAPIKey(models.Model):
    """
    Stores User-Managed API Keys (e.g. Gemini, OpenAI).
    Bring Your Own Key (BYOK) model.
    """
    PROVIDER_GEMINI = "gemini"
    
    PROVIDER_CHOICES = [
        (PROVIDER_GEMINI, "Google Gemini"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="integration_api_keys")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    label = models.CharField(max_length=100, default="My Key")
    
    key_enc = models.TextField(help_text="Encrypted API Key")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ["user", "provider", "label"]

    def set_key(self, raw_key: str):
        cipher = get_cipher_suite()
        self.key_enc = cipher.encrypt(raw_key.encode()).decode()
        
    def get_key(self) -> str:
        cipher = get_cipher_suite()
        return cipher.decrypt(self.key_enc.encode()).decode()
