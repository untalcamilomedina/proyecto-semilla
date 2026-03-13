"""
Community models with Skool-style features.

Enhanced community supporting:
- Spaces (like Skool groups)
- Topics with MDX content
- Posts/comments with reactions
- Gamification (points, levels, leaderboard)
- Member profiles with contribution tracking
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Space(models.Model):
    """Community space (equivalent to Skool's community groups).

    A Space is a themed area within a community. Each tenant can have
    multiple spaces (e.g., "General", "Course Q&A", "Announcements").
    """

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="community_spaces"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True, default="")
    icon_emoji = models.CharField(max_length=10, blank=True, default="💬")
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default space for new members")
    position = models.PositiveIntegerField(default=0)

    # Access control
    is_public = models.BooleanField(default=True)
    requires_level = models.PositiveIntegerField(
        default=0, help_text="Minimum member level to access"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "name"]
        unique_together = [("organization", "slug")]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:200]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.icon_emoji} {self.name}"


class Topic(models.Model):
    """Community topic/thread with MDX content."""

    class TopicType(models.TextChoices):
        DISCUSSION = "discussion", "Discussion"
        QUESTION = "question", "Question"
        POLL = "poll", "Poll"
        ANNOUNCEMENT = "announcement", "Announcement"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="community_topics"
    )
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="topics")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_topics",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, default="")
    content_mdx = models.TextField(blank=True, default="", help_text="MDX content")
    topic_type = models.CharField(
        max_length=20, choices=TopicType.choices, default=TopicType.DISCUSSION
    )

    # Moderation
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False, help_text="For question topics")

    # Engagement metrics (denormalized for performance)
    reply_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_pinned", "-last_activity_at"]
        indexes = [
            models.Index(fields=["organization", "space", "-last_activity_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """Reply/comment on a topic with MDX support."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="community_posts"
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_posts",
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField(help_text="MDX content")

    # Engagement
    like_count = models.PositiveIntegerField(default=0)
    is_answer = models.BooleanField(default=False, help_text="Accepted answer for Q topics")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_answer", "created_at"]

    def __str__(self) -> str:
        return f"{self.topic_id}:{self.author_id}:{self.created_at:%Y-%m-%d}"


class Reaction(models.Model):
    """Emoji reactions on topics and posts (Skool-style likes)."""

    class ReactionType(models.TextChoices):
        LIKE = "like", "👍"
        LOVE = "love", "❤️"
        INSIGHTFUL = "insightful", "💡"
        CELEBRATE = "celebrate", "🎉"

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="community_reactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_reactions"
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, null=True, blank=True, related_name="reactions"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reactions"
    )
    reaction_type = models.CharField(
        max_length=20, choices=ReactionType.choices, default=ReactionType.LIKE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One reaction type per user per target
        constraints = [
            models.UniqueConstraint(
                fields=["user", "topic", "reaction_type"],
                name="unique_topic_reaction",
                condition=models.Q(topic__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "post", "reaction_type"],
                name="unique_post_reaction",
                condition=models.Q(post__isnull=False),
            ),
        ]


class MemberProfile(models.Model):
    """Community member profile with gamification (Skool-style levels)."""

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="community_profiles"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_profile"
    )
    bio = models.TextField(blank=True, default="", max_length=500)
    avatar_url = models.URLField(blank=True, default="")

    # Gamification
    points = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)

    # Contribution tracking
    topics_created = models.PositiveIntegerField(default=0)
    posts_created = models.PositiveIntegerField(default=0)
    likes_received = models.PositiveIntegerField(default=0)
    likes_given = models.PositiveIntegerField(default=0)

    joined_community_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("organization", "user")]
        ordering = ["-points"]

    @property
    def level_name(self) -> str:
        """Skool-style level names."""
        level_names = {
            1: "Newcomer",
            2: "Member",
            3: "Active",
            4: "Contributor",
            5: "Expert",
            6: "Leader",
            7: "Champion",
            8: "Legendary",
        }
        return level_names.get(self.level, f"Level {self.level}")

    def add_points(self, amount: int) -> None:
        """Add points and auto-level up."""
        self.points += amount
        # Level thresholds (Skool-style)
        thresholds = [0, 10, 50, 150, 400, 1000, 2500, 5000]
        for lvl, threshold in enumerate(thresholds, start=1):
            if self.points >= threshold:
                self.level = lvl
        self.save(update_fields=["points", "level"])

    def __str__(self) -> str:
        return f"{self.user.email} (L{self.level})"


# ── Points Configuration ──────────────────────────────────

POINTS_CONFIG = {
    "create_topic": 5,
    "create_post": 2,
    "receive_like": 1,
    "answer_accepted": 10,
    "complete_course": 20,
}
