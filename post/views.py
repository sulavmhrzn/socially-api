from comment.models import Comment
from comment.serializers import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentSerializer,
)
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from like.models import Like
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import PostFilterSet
from .models import Post
from .serializers import PostCreateSerializer, PostListSerializer


class PostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ("title", "author__username", "tags__name")

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        qs = (
            Post.objects.select_related("author")
            .prefetch_related("tags")
            .prefetch_related("comment")
            .prefetch_related("like")
            .filter(is_published=True)
            .all()
        )
        posts = self.filter_queryset(qs)
        serializer = PostListSerializer(
            instance=posts, many=True, context={"request": request}
        )
        return Response(data=serializer.data)

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PostRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id=None):
        post = get_object_or_404(
            Post.objects.select_related("author")
            .prefetch_related("comment")
            .prefetch_related("tags"),
            id=id,
            is_published=True,
        )
        serializer = PostListSerializer(instance=post)
        return Response(data=serializer.data)

    def delete(self, request, id=None):
        try:
            post = get_object_or_404(Post, id=id, author=request.user)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                data={"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

    def put(self, request, id=None):
        post = get_object_or_404(Post, id=id, author=request.user)
        serializer = PostCreateSerializer(instance=post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CommentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(
            Post.objects.select_related("author"), is_published=True, id=post_id
        )
        comments = post.comment.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        get_object_or_404(
            Post,
            id=post_id,
            is_published=True,
        )
        serializer = CommentCreateSerializer(
            data=request.data, context={"post_id": post_id, "user": self.request.user}
        )
        serializer.is_valid()
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class CommentRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, post_id, comment_id):
        # comment_qs = Comment.objects.select_related("user").select_related("post")
        post = get_object_or_404(
            Post.objects.select_related("author"),
            id=post_id,
        )
        comment_qs = post.comment.select_related("user").all()

        comment = get_object_or_404(comment_qs, object_id=post_id, id=comment_id)
        serializer = CommentDetailSerializer(comment, context={"request": request})
        return Response(serializer.data)

    def put(self, request, post_id, comment_id):
        get_object_or_404(
            Post.objects.select_related("author"),
            id=post_id,
        )
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        serializer = CommentCreateSerializer(instance=comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_published=True)
        user = self.request.user
        if post.like.filter(user=user):
            Like.objects.get(user=user).delete()
            return Response({"message": "Like removed"})
        post.like.create(user=user)
        return Response({"message": "Like added"})
