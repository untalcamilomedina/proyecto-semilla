from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from billing.models import Subscription

class MeteringService:
    @staticmethod
    def check_and_track_request(tenant, feature="requests"):
        """
        Checks if the tenant has quota remaining for the feature.
        If yes, increments usage.
        If no, raises PermissionDenied.
        """
        try:
            # Get active subscription
            subscription = Subscription.objects.select_related("plan").get(
                organization=tenant,
                status__in=["active", "trialing"]
            )
        except Subscription.DoesNotExist:
            raise PermissionDenied("No active subscription found.")

        # Reset logic (Naive monthly reset based on creation day)
        # In production, use a periodic task or check `current_period_end`
        # For this MVP, we rely on `usage_reset_at` or manual resets via periodic tasks
        
        limit = subscription.plan.max_requests
        used = subscription.requests_used

        if feature == "diagrams":
            limit = subscription.plan.max_diagrams
            used = subscription.diagrams_used

        if used >= limit:
            raise PermissionDenied(
                f"Usage limit reached for {feature}. Limit: {limit}. Upgrade your plan."
            )

        # Increment
        if feature == "diagrams":
            subscription.diagrams_used += 1
        else:
            subscription.requests_used += 1
        
        subscription.save(update_fields=["diagrams_used", "requests_used"])
