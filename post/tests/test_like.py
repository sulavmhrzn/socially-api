from django.contrib.auth.models import User
from django.urls import reverse
from post.models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class TestLikeCreate(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.user2 = User.objects.create_user(
            username="testuser2", password="testuser2"
        )
        self.post1 = Post.objects.create(
            title="post 1", content="post 1", tags=["post", "one"], author=self.user1
        )
        self.post2 = Post.objects.create(
            title="post 2", content="post 2", tags=["post", "two"], author=self.user2
        )

    def test_create_likes_for_authenticated_user_returns_201(self):
        url = reverse("like_post", kwargs={"post_id": self.post1.id})

        self.client.login(username="testuser", password="testuser")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"message": "Like added"})
        self.assertEqual(self.post1.like.count(), 1)

    def test_create_likes_for_unauthenticated_user_returns_403(self):
        url = reverse("like_post", kwargs={"post_id": self.post1.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.post1.like.count(), 0)

    def test_create_likes_for_same_post_unlike_it(self):
        url = reverse("like_post", kwargs={"post_id": self.post1.id})

        self.client.login(username="testuser", password="testuser")
        self.client.post(url)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"message": "Like removed"})
        self.assertEqual(self.post1.like.count(), 0)
