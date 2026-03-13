"""LMS model translation registration for django-modeltranslation."""

from modeltranslation.translator import TranslationOptions, register

from lms.models import Course, Lesson, Section


@register(Course)
class CourseTranslation(TranslationOptions):
    fields = ("title", "description", "description_mdx")


@register(Section)
class SectionTranslation(TranslationOptions):
    fields = ("title", "description")


@register(Lesson)
class LessonTranslation(TranslationOptions):
    fields = ("title", "content")
