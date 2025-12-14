from __future__ import annotations

from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from multitenant.schema import get_current_schema


def get_default_organization_id() -> int:
    from multitenant.models import Tenant

    schema_name = get_current_schema()
    try:
        return Tenant.objects.only("id").get(schema_name=schema_name).id
    except Tenant.DoesNotExist as exc:
        raise RuntimeError(
            f"Cannot infer tenant organization for schema '{schema_name}'. "
            "Set `organization` explicitly or ensure TenantMiddleware is active."
        ) from exc


class TenantAwarePage(Page):
    organization = models.ForeignKey(
        "multitenant.Tenant",
        on_delete=models.PROTECT,
        related_name="cms_%(class)s_pages",
        default=get_default_organization_id,
        editable=False,
    )

    class Meta:
        abstract = True


class HomePage(TenantAwarePage):
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["cms.ArticleIndexPage"]
    max_count = 1


class ArticleIndexPage(TenantAwarePage):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["cms.HomePage"]
    subpage_types = ["cms.ArticlePage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["articles"] = (
            ArticlePage.objects.child_of(self).live().order_by("-first_published_at")
        )
        return context


class ArticlePage(TenantAwarePage):
    date = models.DateField(default=timezone.now)
    intro = models.CharField(max_length=250, blank=True, default="")
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = ["cms.ArticleIndexPage"]
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("organization"),
    ]
