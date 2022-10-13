from django.contrib.auth.models import User
from post.serializers import (
    CommentDetailSerializer,
    PostDetailSerializer,
    PostListSerializer,
)
from rest_framework import serializers


class DashboardSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_posts(self, obj):
        data = PostDetailSerializer(
            self.context["posts"],
            many=True,
            context={"request": self.context["request"]},
        ).data
        print(data)
        return data

    def get_comments(self, obj):
        return CommentDetailSerializer(
            self.context["comments"],
            many=True,
            context={"request": self.context["request"]},
        ).data

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "posts", "comments"]
