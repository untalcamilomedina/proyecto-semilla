from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ForumViewSet, PostViewSet, TopicViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("forums", ForumViewSet, basename="forums")
router.register("topics", TopicViewSet, basename="topics")
router.register("posts", PostViewSet, basename="posts")

urlpatterns = [
    path("", include(router.urls)),
]
