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
        # Stats Cache
        from django.core.cache import cache
        cache_key = f"dashboard_stats:{tenant.id}"
        stats = cache.get(cache_key)
        
        if not stats:
            total_members = Membership.objects.filter(organization=tenant).count()
            active_members = Membership.objects.filter(organization=tenant, is_active=True).count()
            stats = {
                "total_members": total_members,
                "active_members": active_members,
                "pending_invites": 0,
                "mrr": 0,
            }
            cache.set(cache_key, stats, timeout=60 * 5)  # 5 minutes
        
        # Recent Activity (Optimized - Realtime)
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
            "stats": stats,
            "recent_activity": activity_data,
            "modules_status": {
                "billing": "active",
                "cms": "inactive",
            }
        }
        return Response(data)
