from comment.serializers import CommentDetailSerializer
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from post.serializers import PostDetailSerializer, PostListSerializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator


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


class UserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that email already exists.",
            )
        ]
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
        ]

    def create(self, validated_data):
        password = validated_data["password"]
        password2 = validated_data["password2"]
        email = validated_data["email"]
        if password != password2:
            raise serializers.ValidationError({"msg": "Passwords do not match"})

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=password,
        )
        return user
