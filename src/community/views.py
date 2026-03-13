"""Community viewsets for Skool-style community API."""

from __future__ import annotations

from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import POINTS_CONFIG, MemberProfile, Post, Reaction, Space, Topic
from .serializers import (
    LeaderboardSerializer,
    MemberProfileSerializer,
    PostSerializer,
    ReactionSerializer,
    SpaceSerializer,
    TopicDetailSerializer,
    TopicListSerializer,
)


def request_tenant(request):
    return getattr(request, "tenant", None)


class TenantScopedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_organization(self):
        organization = request_tenant(self.request)
        if organization is None:
            raise NotFound("Tenant required.")
        return organization


class SpaceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    serializer_class = SpaceSerializer
    search_fields = ["name"]

    def get_queryset(self):
        return Space.objects.filter(organization=self.get_organization())

    def perform_create(self, serializer):
        serializer.save(organization=self.get_organization())


class TopicViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    filterset_fields = ["space", "topic_type", "is_pinned", "is_answered"]
    search_fields = ["title"]

    def get_serializer_class(self):
        if self.action == "list":
            return TopicListSerializer
        return TopicDetailSerializer

    def get_queryset(self):
        qs = (
            Topic.objects.filter(organization=self.get_organization())
            .select_related("author", "space")
        )
        return qs

    def perform_create(self, serializer):
        org = self.get_organization()
        serializer.save(organization=org, author=self.request.user)

        # Award points for creating a topic
        profile, _ = MemberProfile.objects.get_or_create(
            organization=org, user=self.request.user
        )
        profile.topics_created += 1
        profile.save(update_fields=["topics_created"])
        profile.add_points(POINTS_CONFIG["create_topic"])

    def retrieve(self, request, *args, **kwargs):
        """Increment view count on retrieve."""
        instance = self.get_object()
        Topic.objects.filter(pk=instance.pk).update(view_count=instance.view_count + 1)
        instance.view_count += 1
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PostViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    serializer_class = PostSerializer
    filterset_fields = ["topic"]

    def get_queryset(self):
        return (
            Post.objects.filter(organization=self.get_organization())
            .select_related("author", "topic")
        )

    def perform_create(self, serializer):
        org = self.get_organization()
        post = serializer.save(organization=org, author=self.request.user)

        # Update topic metrics
        Topic.objects.filter(pk=post.topic_id).update(
            reply_count=post.topic.posts.count(),
            last_activity_at=timezone.now(),
        )

        # Award points
        profile, _ = MemberProfile.objects.get_or_create(
            organization=org, user=self.request.user
        )
        profile.posts_created += 1
        profile.save(update_fields=["posts_created"])
        profile.add_points(POINTS_CONFIG["create_post"])

    @action(detail=True, methods=["post"], url_path="accept-answer")
    def accept_answer(self, request, pk=None):
        """Mark a post as the accepted answer (for question topics)."""
        post = self.get_object()
        if post.topic.topic_type != Topic.TopicType.QUESTION:
            return Response({"detail": "Only question topics can have answers."}, status=400)

        # Unmark previous answers
        Post.objects.filter(topic=post.topic, is_answer=True).update(is_answer=False)

        post.is_answer = True
        post.save(update_fields=["is_answer"])

        post.topic.is_answered = True
        post.topic.save(update_fields=["is_answered"])

        # Award points to answer author
        profile, _ = MemberProfile.objects.get_or_create(
            organization=self.get_organization(), user=post.author
        )
        profile.add_points(POINTS_CONFIG["answer_accepted"])

        return Response({"detail": "Answer accepted."})


class ReactionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    TenantScopedViewSet,
):
    serializer_class = ReactionSerializer

    def get_queryset(self):
        return Reaction.objects.filter(organization=self.get_organization())

    def perform_create(self, serializer):
        org = self.get_organization()
        reaction = serializer.save(organization=org, user=self.request.user)

        # Update like counts
        if reaction.topic:
            Topic.objects.filter(pk=reaction.topic_id).update(
                like_count=reaction.topic.reactions.count()
            )
            # Award points to content author
            target_user = reaction.topic.author
        elif reaction.post:
            Post.objects.filter(pk=reaction.post_id).update(
                like_count=reaction.post.reactions.count()
            )
            target_user = reaction.post.author
        else:
            return

        # Points for giving like
        giver_profile, _ = MemberProfile.objects.get_or_create(
            organization=org, user=self.request.user
        )
        giver_profile.likes_given += 1
        giver_profile.save(update_fields=["likes_given"])

        # Points for receiving like
        if target_user != self.request.user:
            receiver_profile, _ = MemberProfile.objects.get_or_create(
                organization=org, user=target_user
            )
            receiver_profile.likes_received += 1
            receiver_profile.save(update_fields=["likes_received"])
            receiver_profile.add_points(POINTS_CONFIG["receive_like"])


class MemberProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    TenantScopedViewSet,
):
    serializer_class = MemberProfileSerializer

    def get_queryset(self):
        return (
            MemberProfile.objects.filter(organization=self.get_organization())
            .select_related("user")
        )

    @action(detail=False, methods=["get"], url_path="me")
    def my_profile(self, request):
        """Get or create the current user's community profile."""
        profile, _ = MemberProfile.objects.get_or_create(
            organization=self.get_organization(),
            user=request.user,
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="leaderboard")
    def leaderboard(self, request):
        """Top 20 members by points."""
        profiles = (
            MemberProfile.objects.filter(organization=self.get_organization())
            .select_related("user")
            .order_by("-points")[:20]
        )
        serializer = LeaderboardSerializer(profiles, many=True)
        return Response(serializer.data)
