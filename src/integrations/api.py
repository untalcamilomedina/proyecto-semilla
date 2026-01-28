from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Diagram, Job
from .schemas import FlowSpec, ERDSpec
from rest_framework import serializers

# --- Serializers ---

class DiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagram
        fields = ["id", "name", "description", "type", "spec", "is_public", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "type", "status", "progress", "result", "error", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "progress", "result", "error", "created_at", "updated_at"]

# --- ViewSets ---

class DiagramViewSet(viewsets.ModelViewSet):
    """
    CRUD for Diagrams (Flow & ERD).
    """
    queryset = Diagram.objects.all()
    serializer_class = DiagramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to Async Jobs status.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
