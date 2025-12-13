from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from billing.webhooks import WebhookError, construct_event, handle_event


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    try:
        event = construct_event(
            payload=request.body, sig_header=request.headers.get("Stripe-Signature")
        )
    except WebhookError:
        return HttpResponse(status=400)

    handle_event(event)
    return HttpResponse(status=200)
