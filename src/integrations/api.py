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

from asgiref.sync import async_to_sync
from .notion.services import NotionService
from .schemas import ERDSpec

class NotionIntegrationViewSet(viewsets.ViewSet):
    """
    ViewSet for Notion Integration actions (Scan, Apply).
    Uses async_to_sync to bridge Sync ViewSet -> Async Service.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"])
    def scan(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)
            
        try:
            # Sync wrapper around async service
            spec = async_to_sync(NotionService.scan_databases)(token)
            return Response(spec.model_dump())
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"])
    def apply_erd(self, request):
        token = request.data.get("token")
        spec_data = request.data.get("spec")
        parent_page_id = request.data.get("parent_page_id")
        
        if not token or not spec_data or not parent_page_id:
            return Response({"error": "Missing required fields"}, status=400)
            
        try:
            spec = ERDSpec(**spec_data)
            created_ids = async_to_sync(NotionService.apply_erd)(token, parent_page_id, spec)
            return Response({"created_databases": created_ids})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

from .miro.services import MiroService

class MiroIntegrationViewSet(viewsets.ViewSet):
    """
    ViewSet for Miro Integration actions (Export/Import).
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"])
    def export_erd(self, request):
        token = request.data.get("token")
        board_id = request.data.get("board_id")
        spec_data = request.data.get("spec")
        
        if not token or not board_id or not spec_data:
            return Response({"error": "Missing required fields"}, status=400)
            
        try:
            spec = ERDSpec(**spec_data)
            result = async_to_sync(MiroService.export_erd_to_board)(token, board_id, spec)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"])
    def import_erd(self, request):
        token = request.data.get("token")
        board_id = request.data.get("board_id")
        
        if not token or not board_id:
            return Response({"error": "Missing required fields"}, status=400)
            
        try:
            # Sync wrapper around async service
            spec = async_to_sync(MiroService.import_from_miro)(token, board_id)
            return Response(spec.model_dump())
        except Exception as e:
            return Response({"error": str(e)}, status=500)
