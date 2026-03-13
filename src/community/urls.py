"""Community URL configuration."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from community.views import (
    MemberProfileViewSet,
    PostViewSet,
    ReactionViewSet,
    SpaceViewSet,
    TopicViewSet,
)

router = DefaultRouter()
router.register("spaces", SpaceViewSet, basename="community-space")
router.register("topics", TopicViewSet, basename="community-topic")
router.register("posts", PostViewSet, basename="community-post")
router.register("reactions", ReactionViewSet, basename="community-reaction")
router.register("members", MemberProfileViewSet, basename="community-member")

urlpatterns = [
    path("", include(router.urls)),
]
