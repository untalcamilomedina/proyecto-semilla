from rest_framework import viewsets, permissions
from rest_framework.response import Response
from core.models import Membership, RoleAuditLog
from billing.models import Subscription

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Return real summary statistics for the dashboard.
        """
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return Response({"error": "No tenant found"}, status=400)

        # Stats
        total_members = Membership.objects.filter(organization=tenant).count()
        active_members = Membership.objects.filter(organization=tenant, is_active=True).count()
        
        # Recent Activity (Optimized)
        recent_logs = RoleAuditLog.objects.filter(organization=tenant)\
            .select_related('actor', 'role')\
            .order_by('-created_at')[:5]
        
        activity_data = []
        for log in recent_logs:
            activity_data.append({
                "id": log.id,
                "action": log.get_action_display(),
                "actor": log.actor.email if log.actor else "System",
                "role": log.role.name if log.role else "-",
                "timestamp": log.created_at
            })

        data = {
            "stats": {
                "total_members": total_members,
                "active_members": active_members,
                "pending_invites": 0,  # Placeholder until Invite model exists
                "mrr": 0,  # Placeholder
            },
            "recent_activity": activity_data,
            "modules_status": {
                "billing": "active", # Always active in this version
                "cms": "inactive",
            }
        }
        return Response(data)
