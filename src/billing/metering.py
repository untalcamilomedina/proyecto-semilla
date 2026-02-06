from django.db.models import F
from rest_framework.exceptions import PermissionDenied

from billing.models import Subscription


class MeteringService:
    @staticmethod
    def check_and_track_request(tenant, feature="requests"):
        """
        Checks if the tenant has quota remaining for the feature.
        If yes, atomically increments usage with F() to prevent race conditions.
        If no, raises PermissionDenied.
        """
        try:
            subscription = Subscription.objects.select_related("plan").get(
                organization=tenant,
                status__in=["active", "trialing"],
            )
        except Subscription.DoesNotExist:
            raise PermissionDenied("No active subscription found.")

        if feature == "diagrams":
            limit = subscription.plan.max_diagrams
            used = subscription.diagrams_used
        else:
            limit = subscription.plan.max_requests
            used = subscription.requests_used

        if used >= limit:
            raise PermissionDenied(
                f"Usage limit reached for {feature}. Limit: {limit}. Upgrade your plan."
            )

        # Atomic increment using F() to prevent race conditions under concurrency
        field = "diagrams_used" if feature == "diagrams" else "requests_used"
        Subscription.objects.filter(pk=subscription.pk).update(
            **{field: F(field) + 1}
        )
