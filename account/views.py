from post.models import Comment, Post
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DashboardSerializer


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        posts = (
            Post.objects.select_related("author")
            .prefetch_related("tags")
            .prefetch_related("comment_set")
            .filter(author=user)
            .all()
        )
        comments = (
            Comment.objects.select_related("user")
            .select_related("post")
            .filter(user=user)
            .all()
        )
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
