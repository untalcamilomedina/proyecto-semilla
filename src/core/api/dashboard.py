from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Return summary statistics for the dashboard.
        """
        # TODO: Replace with real queries to DB
        data = {
            "stats": {
                "total_members": 12,
                "active_members": 8,
                "pending_invites": 4,
                "mrr": 0,  # Monthly Recurring Revenue
            },
            "recent_activity": [
                {"id": 1, "action": "user_joined", "user": "alice@example.com", "timestamp": "2023-10-27T10:00:00Z"},
                {"id": 2, "action": "role_updated", "roll": "Admin", "timestamp": "2023-10-26T14:30:00Z"},
            ],
            "modules_status": {
                "cms": "active",
                "lms": "inactive",
            }
        }
        return Response(data)
