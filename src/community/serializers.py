from __future__ import annotations

from rest_framework import serializers

from .models import Forum, Post, Topic


class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = ["id", "name", "description", "is_active"]


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "forum", "author", "title", "is_pinned", "is_locked"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["forum"].queryset = Forum.objects.none()
        else:
            self.fields["forum"].queryset = Forum.objects.filter(organization=tenant)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "topic", "author", "content", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        if tenant is None:
            self.fields["topic"].queryset = Topic.objects.none()
        else:
            self.fields["topic"].queryset = Topic.objects.filter(organization=tenant)
