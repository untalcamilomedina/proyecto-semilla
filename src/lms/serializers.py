"""LMS serializers for course management API."""

from __future__ import annotations

from rest_framework import serializers

from .models import Certificate, Course, Enrollment, Lesson, LessonProgress, Review, Section


class SectionSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ["id", "course", "title", "description", "order", "lesson_count"]

    def get_lesson_count(self, obj: Section) -> int:
        return obj.lessons.count()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["course"].queryset = Course.objects.none()
        else:
            self.fields["course"].queryset = Course.objects.filter(organization=tenant)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id", "course", "section", "title", "slug", "order",
            "content_type", "content", "video_url", "duration_minutes",
            "is_preview", "is_published",
        ]
        read_only_fields = ["slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["course"].queryset = Course.objects.none()
        else:
            self.fields["course"].queryset = Course.objects.filter(organization=tenant)


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight serializer without content body for listings."""

    class Meta:
        model = Lesson
        fields = [
            "id", "course", "section", "title", "slug", "order",
            "content_type", "video_url", "duration_minutes",
            "is_preview", "is_published",
        ]


class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight course serializer for listings."""
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description", "thumbnail_url",
            "status", "is_featured", "is_published", "pricing_type",
            "price", "currency", "level", "estimated_hours", "tags",
            "instructor_name", "published_at", "created_at",
        ]
        read_only_fields = ["slug", "published_at", "created_at"]

    def get_instructor_name(self, obj: Course) -> str:
        if obj.instructor:
            return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip() or obj.instructor.email
        return ""


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course serializer with MDX description and nested sections."""
    instructor_name = serializers.SerializerMethodField()
    sections = SectionSerializer(many=True, read_only=True)
    total_lessons = serializers.ReadOnlyField()
    total_enrolled = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description", "description_mdx",
            "thumbnail_url", "preview_video_url", "status", "is_featured",
            "is_published", "pricing_type", "price", "currency",
            "stripe_price_id", "stripe_product_id", "level",
            "estimated_hours", "tags", "requirements", "what_you_learn",
            "instructor", "instructor_name", "sections",
            "total_lessons", "total_enrolled",
            "published_at", "created_at", "updated_at",
        ]
        read_only_fields = [
            "slug", "published_at", "created_at", "updated_at",
            "total_lessons", "total_enrolled",
        ]

    def get_instructor_name(self, obj: Course) -> str:
        if obj.instructor:
            return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip() or obj.instructor.email
        return ""


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id", "user", "course", "course_title", "status", "progress",
            "amount_paid", "currency", "stripe_payment_intent_id",
            "enrolled_at", "completed_at",
        ]
        read_only_fields = [
            "enrolled_at", "completed_at", "progress", "course_title",
        ]

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
        fields = ["id", "enrollment", "lesson", "completed_at", "time_spent_seconds"]

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
            raise serializers.ValidationError(
                {"lesson": "Lesson must belong to the enrollment course."}
            )
        return attrs


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="enrollment.course.title", read_only=True)
    user_email = serializers.EmailField(source="enrollment.user.email", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id", "enrollment", "certificate_number", "issued_at",
            "pdf_url", "course_title", "user_email",
        ]
        read_only_fields = ["certificate_number", "issued_at"]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id", "user", "course", "rating", "comment",
            "user_name", "created_at", "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_user_name(self, obj: Review) -> str:
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email

    def validate_rating(self, value: int) -> int:
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
