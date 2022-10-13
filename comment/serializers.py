from post.models import Post
from rest_framework import serializers

from .models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]

    def create(self, validated_data):
        post = Post.objects.get(id=self.context["post_id"])
        post.comment.create(
            content=self.validated_data["content"], user=self.context["user"]
        )
        return {"content": self.validated_data["content"]}


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ["id", "content", "user", "created_at", "updated_at"]


class CommentDetailSerializer(serializers.HyperlinkedModelSerializer):

    user = serializers.StringRelatedField()
    post = serializers.HyperlinkedRelatedField(
        view_name="post_retrieve_update_delete", read_only=True, lookup_field="id"
    )

    class Meta:
        model = Comment
        fields = ["id", "content", "user", "post", "created_at", "updated_at"]
