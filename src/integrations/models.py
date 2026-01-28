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
