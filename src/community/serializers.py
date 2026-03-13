"""Community serializers for Skool-style community API."""

from __future__ import annotations

from rest_framework import serializers

from .models import MemberProfile, Post, Reaction, Space, Topic


class SpaceSerializer(serializers.ModelSerializer):
    topic_count = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            "id", "name", "slug", "description", "icon_emoji",
            "is_active", "is_default", "is_public", "requires_level",
            "position", "topic_count", "created_at",
        ]
        read_only_fields = ["slug", "created_at"]

    def get_topic_count(self, obj: Space) -> int:
        return obj.topics.count()


class TopicListSerializer(serializers.ModelSerializer):
    """Lightweight topic serializer for listings."""
    author_name = serializers.SerializerMethodField()
    space_name = serializers.CharField(source="space.name", read_only=True)

    class Meta:
        model = Topic
        fields = [
            "id", "space", "space_name", "title", "slug", "topic_type",
            "is_pinned", "is_locked", "is_answered",
            "reply_count", "like_count", "view_count",
            "author", "author_name",
            "created_at", "last_activity_at",
        ]
        read_only_fields = [
            "slug", "reply_count", "like_count", "view_count",
            "created_at", "last_activity_at",
        ]

    def get_author_name(self, obj: Topic) -> str:
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email


class TopicDetailSerializer(serializers.ModelSerializer):
    """Full topic serializer with MDX content."""
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "id", "space", "title", "slug", "content_mdx", "topic_type",
            "is_pinned", "is_locked", "is_answered",
            "reply_count", "like_count", "view_count",
            "author", "author_name",
            "created_at", "updated_at", "last_activity_at",
        ]
        read_only_fields = [
            "slug", "reply_count", "like_count", "view_count",
            "created_at", "updated_at", "last_activity_at",
        ]

    def get_author_name(self, obj: Topic) -> str:
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "topic", "author", "author_name", "parent",
            "content", "like_count", "is_answer",
            "reply_count", "created_at", "updated_at",
        ]
        read_only_fields = ["author", "like_count", "created_at", "updated_at"]

    def get_author_name(self, obj: Post) -> str:
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email

    def get_reply_count(self, obj: Post) -> int:
        return obj.replies.count()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["topic"].queryset = Topic.objects.none()
        else:
            self.fields["topic"].queryset = Topic.objects.filter(organization=tenant)


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["id", "user", "topic", "post", "reaction_type", "created_at"]
        read_only_fields = ["user", "created_at"]

    def validate(self, attrs):
        if not attrs.get("topic") and not attrs.get("post"):
            raise serializers.ValidationError("Either topic or post must be specified.")
        if attrs.get("topic") and attrs.get("post"):
            raise serializers.ValidationError("Cannot react to both topic and post.")
        return attrs


class MemberProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    level_name = serializers.ReadOnlyField()

    class Meta:
        model = MemberProfile
        fields = [
            "id", "user", "user_email", "user_name", "bio", "avatar_url",
            "points", "level", "level_name",
            "topics_created", "posts_created", "likes_received", "likes_given",
            "joined_community_at", "last_active_at",
        ]
        read_only_fields = [
            "user", "points", "level", "topics_created", "posts_created",
            "likes_received", "likes_given", "joined_community_at", "last_active_at",
        ]

    def get_user_name(self, obj: MemberProfile) -> str:
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class LeaderboardSerializer(serializers.ModelSerializer):
    """Lightweight serializer for leaderboard display."""
    user_name = serializers.SerializerMethodField()
    level_name = serializers.ReadOnlyField()

    class Meta:
        model = MemberProfile
        fields = ["user", "user_name", "points", "level", "level_name", "avatar_url"]

    def get_user_name(self, obj: MemberProfile) -> str:
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
