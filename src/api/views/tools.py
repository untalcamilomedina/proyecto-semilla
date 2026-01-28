from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .services import NotionService
from .models import ToolConfiguration

class NotionToolViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def databases(self, request):
        service = NotionService(request.user)
        data = service.list_databases()
        return Response(data)

    @action(detail=True, methods=['get'])
    def schema(self, request, pk=None):
        service = NotionService(request.user)
        data = service.get_database(pk)
        return Response(data)
