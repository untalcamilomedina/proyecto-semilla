"""
Tests for enhanced LMS and Community modules.

Covers model logic, serializer validation, and gamification engine.
"""

import pytest
from django.test import TestCase

from common.encryption import decrypt_value, encrypt_value


# ── LMS Model Tests ─────────────────────────────────────────

class TestLMSModels:
    """Test LMS model logic."""

    def test_course_status_choices(self):
        from lms.models import Course
        assert Course.Status.DRAFT == "draft"
        assert Course.Status.PUBLISHED == "published"
        assert Course.Status.ARCHIVED == "archived"

    def test_course_pricing_types(self):
        from lms.models import Course
        assert Course.PricingType.FREE == "free"
        assert Course.PricingType.PAID == "paid"
        assert Course.PricingType.SUBSCRIPTION == "subscription"

    def test_course_is_free_property(self):
        from lms.models import Course
        course = Course(pricing_type="free")
        assert course.is_free is True
        course.pricing_type = "paid"
        assert course.is_free is False

    def test_lesson_content_types(self):
        from lms.models import Lesson
        assert Lesson.ContentType.VIDEO == "video"
        assert Lesson.ContentType.TEXT == "text"
        assert Lesson.ContentType.QUIZ == "quiz"
        assert Lesson.ContentType.ASSIGNMENT == "assignment"

    def test_enrollment_status_choices(self):
        from lms.models import Enrollment
        assert Enrollment.Status.ACTIVE == "active"
        assert Enrollment.Status.COMPLETED == "completed"
        assert Enrollment.Status.EXPIRED == "expired"
        assert Enrollment.Status.REFUNDED == "refunded"


# ── Community Model Tests ───────────────────────────────────

class TestCommunityModels:
    """Test Community Skool-style model logic."""

    def test_topic_types(self):
        from community.models import Topic
        assert Topic.TopicType.DISCUSSION == "discussion"
        assert Topic.TopicType.QUESTION == "question"
        assert Topic.TopicType.POLL == "poll"
        assert Topic.TopicType.ANNOUNCEMENT == "announcement"

    def test_reaction_types(self):
        from community.models import Reaction
        assert Reaction.ReactionType.LIKE == "like"
        assert Reaction.ReactionType.LOVE == "love"
        assert Reaction.ReactionType.INSIGHTFUL == "insightful"
        assert Reaction.ReactionType.CELEBRATE == "celebrate"

    def test_member_profile_level_names(self):
        from community.models import MemberProfile
        profile = MemberProfile()
        profile.level = 1
        assert profile.level_name == "Newcomer"
        profile.level = 5
        assert profile.level_name == "Expert"
        profile.level = 8
        assert profile.level_name == "Legendary"
        profile.level = 99
        assert profile.level_name == "Level 99"

    def test_points_config_exists(self):
        from community.models import POINTS_CONFIG
        assert "create_topic" in POINTS_CONFIG
        assert "create_post" in POINTS_CONFIG
        assert "receive_like" in POINTS_CONFIG
        assert "answer_accepted" in POINTS_CONFIG
        assert "complete_course" in POINTS_CONFIG
        assert all(isinstance(v, int) and v > 0 for v in POINTS_CONFIG.values())


# ── Serializer Validation Tests ─────────────────────────────

@pytest.mark.django_db
class TestLMSSerializerValidation:
    """Test LMS serializer validation rules."""

    def test_review_serializer_rating_validation(self):
        from lms.serializers import ReviewSerializer
        serializer = ReviewSerializer(data={"rating": 0, "course": 1})
        assert serializer.is_valid() is False

    def test_review_serializer_valid_rating(self):
        from lms.serializers import ReviewSerializer
        serializer = ReviewSerializer(data={"rating": 5, "course": 1, "comment": "Great!"})
        is_valid = serializer.is_valid()
        # Will fail FK validation (course=1 doesn't exist), but rating should be fine
        assert "rating" not in serializer.errors


@pytest.mark.django_db
class TestCommunitySerializerValidation:
    """Test Community serializer validation rules."""

    def test_reaction_requires_target(self):
        from community.serializers import ReactionSerializer
        serializer = ReactionSerializer(data={"reaction_type": "like"})
        assert serializer.is_valid() is False

    def test_reaction_cannot_have_both_targets(self):
        from community.serializers import ReactionSerializer
        serializer = ReactionSerializer(data={
            "reaction_type": "like", "topic": 1, "post": 1
        })
        assert serializer.is_valid() is False


# ── RLS Tests (updated for new tables) ──────────────────────

class TestRLSUpdated:
    """Test RLS covers all new tables."""

    def test_rls_covers_lms_tables(self):
        from common.rls import TENANT_SCOPED_TABLES
        assert "lms_section" in TENANT_SCOPED_TABLES
        assert "lms_certificate" in TENANT_SCOPED_TABLES
        assert "lms_review" in TENANT_SCOPED_TABLES

    def test_rls_covers_community_tables(self):
        from common.rls import TENANT_SCOPED_TABLES
        assert "community_space" in TENANT_SCOPED_TABLES
        assert "community_reaction" in TENANT_SCOPED_TABLES
        assert "community_memberprofile" in TENANT_SCOPED_TABLES
        # Old names should NOT be present
        assert "community_forum" not in TENANT_SCOPED_TABLES

    def test_total_rls_tables(self):
        from common.rls import TENANT_SCOPED_TABLES
        # Should be 31 total tables (core=7, billing=4, api=1, cms=3, lms=7, community=5, mcp=4)
        assert len(TENANT_SCOPED_TABLES) == 31


# ── Encryption Tests ────────────────────────────────────────

class TestEncryptionAdditional:
    """Additional encryption edge cases."""

    def test_long_key_roundtrip(self):
        """Test encryption handles long strings."""
        long_key = "sk_live_" + "a" * 500
        encrypted = encrypt_value(long_key)
        decrypted = decrypt_value(encrypted)
        assert decrypted == long_key

    def test_json_payload_encryption(self):
        """Test encrypting JSON-like strings."""
        import json
        payload = json.dumps({"key": "value", "nested": {"a": 1}})
        encrypted = encrypt_value(payload)
        decrypted = decrypt_value(encrypted)
        assert json.loads(decrypted) == {"key": "value", "nested": {"a": 1}}


# ── CMS Model Tests (additional) ───────────────────────────

class TestCMSModelsAdditional:
    """Additional CMS model tests."""

    def test_content_page_frontmatter_default(self):
        from cms.models import ContentPage
        page = ContentPage()
        assert page.frontmatter == {}
        assert page.tags == []

    def test_content_page_seo_fields_default_empty(self):
        from cms.models import ContentPage
        page = ContentPage()
        assert page.seo_title == ""
        assert page.seo_description == ""
        assert page.og_image_url == ""
