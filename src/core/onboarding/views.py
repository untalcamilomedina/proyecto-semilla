from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from core.models import OnboardingState
from core.services.onboarding import (
    invite_members,
    mark_stripe_connected,
    set_custom_domain,
    set_modules,
    start_onboarding,
)
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context

from .forms import (
    CustomDomainForm,
    InviteMembersForm,
    ModulesForm,
    StartOnboardingForm,
    StripeConnectForm,
)


def _get_state_from_session(request: HttpRequest) -> OnboardingState | None:
    state_id = request.session.get("onboarding_state_id")
    if not state_id:
        return None
    with schema_context(PUBLIC_SCHEMA_NAME):
        try:
            return OnboardingState.objects.select_related("tenant").get(id=state_id)
        except OnboardingState.DoesNotExist:
            return None


class StartView(View):
    template_name = "core/onboarding/start.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, {"form": StartOnboardingForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = StartOnboardingForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        result = start_onboarding(
            org_name=form.cleaned_data["org_name"],
            subdomain=form.cleaned_data["subdomain"],
            admin_email=form.cleaned_data["admin_email"],
            password=form.cleaned_data["password1"],
        )
        request.session["onboarding_state_id"] = result.state.id
        return redirect("core:onboarding_modules")


class ResumeView(View):
    def get(self, request: HttpRequest, token: str) -> HttpResponse:
        with schema_context(PUBLIC_SCHEMA_NAME):
            try:
                state = OnboardingState.objects.select_related("tenant").get(
                    data__resume_token=token, is_complete=False
                )
            except OnboardingState.DoesNotExist:
                return redirect("core:onboarding_start")

        request.session["onboarding_state_id"] = state.id
        step_to_url = {
            1: "core:onboarding_start",
            2: "core:onboarding_modules",
            3: "core:onboarding_stripe",
            4: "core:onboarding_domain",
            5: "core:onboarding_invite",
        }
        return redirect(step_to_url.get(state.current_step, "core:onboarding_start"))


class ModulesView(View):
    template_name = "core/onboarding/modules.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        form = ModulesForm(initial={"modules": state.data.get("modules", [])})
        return render(request, self.template_name, {"form": form, "state": state})

    def post(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        form = ModulesForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "state": state})
        set_modules(state, form.cleaned_data["modules"])
        return redirect("core:onboarding_stripe")


class StripeView(View):
    template_name = "core/onboarding/stripe.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        form = StripeConnectForm(initial={"stripe_connected": state.data.get("stripe_connected")})
        return render(request, self.template_name, {"form": form, "state": state})

    def post(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        form = StripeConnectForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "state": state})
        mark_stripe_connected(state, form.cleaned_data.get("stripe_connected", False))
        return redirect("core:onboarding_domain")


class DomainView(View):
    template_name = "core/onboarding/domain.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        form = CustomDomainForm()
        return render(
            request,
            self.template_name,
            {"form": form, "state": state, "DOMAIN_BASE": getattr(settings, "DOMAIN_BASE", "acme.dev")},
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        form = CustomDomainForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "state": state})
        set_custom_domain(state, form.cleaned_data.get("custom_domain") or None)
        return redirect("core:onboarding_invite")


class InviteView(View):
    template_name = "core/onboarding/invite.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        return render(
            request, self.template_name, {"form": InviteMembersForm(), "state": state}
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        state = _get_state_from_session(request)
        if not state:
            return redirect("core:onboarding_start")
        form = InviteMembersForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "state": state})
        invite_members(state, form.cleaned_data["emails"])
        request.session.pop("onboarding_state_id", None)
        return redirect(reverse("core:onboarding_done"))


class DoneView(View):
    template_name = "core/onboarding/done.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)
