from __future__ import annotations

from django.urls import path

from .views import DoneView, DomainView, InviteView, ModulesView, ResumeView, StartView, StripeView

urlpatterns = [
    path("", StartView.as_view(), name="onboarding_start"),
    path("resume/<str:token>/", ResumeView.as_view(), name="onboarding_resume"),
    path("modules/", ModulesView.as_view(), name="onboarding_modules"),
    path("stripe/", StripeView.as_view(), name="onboarding_stripe"),
    path("domain/", DomainView.as_view(), name="onboarding_domain"),
    path("invite/", InviteView.as_view(), name="onboarding_invite"),
    path("done/", DoneView.as_view(), name="onboarding_done"),
]
