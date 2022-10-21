from comment.models import Comment
from post.models import Post
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DashboardSerializer, UserCreateSerializer


class UserCreateAPIView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        posts = (
            Post.objects.select_related("author")
            .prefetch_related("tags")
            .prefetch_related("comment")
            .prefetch_related("like")
            .filter(author=user)
            .all()
        )
        comments = Comment.objects.select_related("user").filter(user=user).all()

        serializer = DashboardSerializer(
            user,
            context={
                "request": request,
                "user": user,
                "posts": posts,
                "comments": comments,
            },
        )
        return Response(serializer.data)
