from django.urls import path

from . import views

urlpatterns = [
    path("", views.PostListCreateAPIView.as_view(), name="post_list_create"),
    path(
        "<int:id>/",
        views.PostRetrieveUpdateDeleteAPIView.as_view(),
        name="post_retrieve_update_delete",
    ),
    path(
        "<int:post_id>/comments/",
        views.CommentListCreateAPIView.as_view(),
        name="comment_list_create",
    ),
    path(
        "<int:post_id>/comments/<int:comment_id>/",
        views.CommentRetrieveUpdateDeleteAPIView.as_view(),
        name="comment_retrieve_update_delete",
    ),
    path("<int:post_id>/like", views.LikePostAPIView.as_view(), name="like_post"),
]
