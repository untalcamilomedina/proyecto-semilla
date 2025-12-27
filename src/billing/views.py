from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# from billing.webhooks import WebhookError, construct_event, handle_event

@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """
    Deprecated: Use djstripe webhook handler.
    Access at /stripe/webhook/
    """
    return HttpResponse("Deprecated. Use /stripe/webhook/", status=410)
