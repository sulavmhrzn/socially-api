from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Post


class PostCreateSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = ["title", "content", "tags", "is_published"]


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    tags = TagListSerializerField()
    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comment.count()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "tags",
            "author",
            "comment_count",
            "created_at",
            "updated_at",
        ]


class PostDetailSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.StringRelatedField()
    tags = TagListSerializerField()
    comment_count = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        view_name="post_retrieve_update_delete", lookup_field="id", read_only=True
    )

    def get_comment_count(self, obj):
        return obj.comment.count()

    class Meta:
        model = Post
        fields = [
            "url",
            "id",
            "title",
            "content",
            "tags",
            "author",
            "comment_count",
            "created_at",
            "updated_at",
        ]


