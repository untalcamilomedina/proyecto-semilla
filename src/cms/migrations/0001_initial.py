from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import wagtail.fields

import cms.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("multitenant", "0003_branding"),
        ("wagtailcore", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        default=cms.models.get_default_organization_id,
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cms_%(class)s_pages",
                        to="multitenant.tenant",
                    ),
                ),
                ("intro", wagtail.fields.RichTextField(blank=True)),
                ("body", wagtail.fields.RichTextField(blank=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="ArticleIndexPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        default=cms.models.get_default_organization_id,
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cms_%(class)s_pages",
                        to="multitenant.tenant",
                    ),
                ),
                ("intro", wagtail.fields.RichTextField(blank=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="ArticlePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        default=cms.models.get_default_organization_id,
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cms_%(class)s_pages",
                        to="multitenant.tenant",
                    ),
                ),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("intro", models.CharField(blank=True, default="", max_length=250)),
                ("body", wagtail.fields.RichTextField(blank=True)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        ),
    ]
