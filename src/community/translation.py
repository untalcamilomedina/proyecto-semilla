"""Community model translation registration for django-modeltranslation."""

from modeltranslation.translator import TranslationOptions, register

from community.models import Space


@register(Space)
class SpaceTranslation(TranslationOptions):
    fields = ("name", "description")
