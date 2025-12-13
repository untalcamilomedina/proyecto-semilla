from __future__ import annotations

from allauth.account.views import LoginView, SignupView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


class RateLimitedLoginView(LoginView):
    """
    Wrap allauth LoginView with IP-based rate limiting for POST attempts.
    """

    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class RateLimitedSignupView(SignupView):
    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
