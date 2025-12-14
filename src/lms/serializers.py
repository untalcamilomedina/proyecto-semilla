from __future__ import annotations

from rest_framework import serializers

from .models import Course, Enrollment, Lesson, LessonProgress


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "is_published"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "order", "content"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["course"].queryset = Course.objects.none()
        else:
            self.fields["course"].queryset = Course.objects.filter(organization=tenant)


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "user", "course", "enrolled_at", "progress"]
        read_only_fields = ["enrolled_at", "progress"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["course"].queryset = Course.objects.none()
        else:
            self.fields["course"].queryset = Course.objects.filter(organization=tenant)


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ["id", "enrollment", "lesson", "completed_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["enrollment"].queryset = Enrollment.objects.none()
            self.fields["lesson"].queryset = Lesson.objects.none()
        else:
            self.fields["enrollment"].queryset = Enrollment.objects.filter(organization=tenant)
            self.fields["lesson"].queryset = Lesson.objects.filter(organization=tenant)

    def validate(self, attrs):
        enrollment = attrs.get("enrollment") or getattr(self.instance, "enrollment", None)
        lesson = attrs.get("lesson") or getattr(self.instance, "lesson", None)
        if enrollment and lesson and enrollment.course_id != lesson.course_id:
            raise serializers.ValidationError({"lesson": "Lesson must belong to the enrollment course."})
        return attrs
