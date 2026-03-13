"""CMS model translation registration for django-modeltranslation."""

from modeltranslation.translator import TranslationOptions, register

from cms.models import Category, ContentPage


@register(Category)
class CategoryTranslation(TranslationOptions):
    fields = ("name", "description")


@register(ContentPage)
class ContentPageTranslation(TranslationOptions):
    fields = ("title", "excerpt", "body_mdx", "seo_title", "seo_description")
