from django.contrib.auth.models import User
from django.urls import reverse
from post.models import Comment, Post
from rest_framework import status
from rest_framework.test import APITestCase


class TestCommentCreate(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.user2 = User.objects.create_user(
            username="testuser2", password="testuser2"
        )
        self.data = {
            "title": "test post",
            "content": "test post content",
            "tags": ["test", "tags"],
        }
        self.comment = {"content": "nice post"}

    def create_post(self):
        url = reverse("post_list_create")
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(url, data=self.data, format="json")
        return response

    def test_create_comment_returns_201_for_authenticated_user(self):
        self.create_post()
        post = Post.objects.first()
        url = reverse("comment_list_create", kwargs={"post_id": post.id})

        response = self.client.post(url, data=self.comment, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), self.comment)

    def test_create_comment_returns_403_for_unauthenticated_user(self):
        self.create_post()
        post = Post.objects.first()
        url = reverse("comment_list_create", kwargs={"post_id": post.id})

        self.client.logout()
        response = self.client.post(url, data=self.comment, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment_in_correct_post(self):
        self.create_post()
        self.create_post()
        post = Post.objects.first()
        l_post = Post.objects.last()
        url = reverse("comment_list_create", kwargs={"post_id": post.id})

        response = self.client.post(url, data=self.comment, format="json")

        self.assertEqual(post.comment.count(), 1)
        self.assertEqual(l_post.comment.count(), 0)

    def test_create_comment_belongs_to_correct_user(self):
        self.create_post()
        self.create_post()
        post = Post.objects.first()
        l_post = Post.objects.last()

        url = reverse("comment_list_create", kwargs={"post_id": post.id})
        self.client.post(url, data=self.comment, format="json")

        url2 = reverse("comment_list_create", kwargs={"post_id": l_post.id})
        self.client.login(username="testuser2", password="testuser2")
        self.client.post(url2, data=self.comment, format="json")

        self.assertEqual(post.comment.first().user, self.user1)
        self.assertEqual(post.comment.first().object_id, post.id)
        self.assertEqual(l_post.comment.first().user, self.user2)
        self.assertNotEqual(l_post.comment.first().user, self.user1)

    def test_create_comment_cannot_be_created_in_unpublished_post(self):
        data2 = self.data.copy()
        data2["is_published"] = False
        post = Post.objects.create(**data2, author=self.user1)
        url = reverse("comment_list_create", kwargs={"post_id": post.id})
        response = self.client.post(url, data=self.comment, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(post.comment.count(), 0)


class TestCommentList(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.user2 = User.objects.create_user(
            username="testuser2", password="testuser2"
        )
        self.data = {
            "title": "test post",
            "content": "test post content",
            "tags": ["test", "tags"],
        }
        self.comment = {"content": "nice post"}

    def create_post(self):
        url = reverse("post_list_create")
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(url, data=self.data, format="json")
        return response

    def create_comments(self):
        """
        Create two post and 3 comments, 2 for first post and 1 for last
        """
        self.create_post()
        self.create_post()

        self.p1 = Post.objects.first()
        self.p2 = Post.objects.last()

        url = reverse("comment_list_create", kwargs={"post_id": self.p1.id})
        url2 = reverse("comment_list_create", kwargs={"post_id": self.p2.id})

        self.client.post(url, data=self.comment, format="json")
        self.client.post(url, data=self.comment, format="json")

        self.client.post(url2, data=self.comment, format="json")

    def test_comments_list_for_proper_post(self):
        self.create_comments()

        url = reverse("comment_list_create", kwargs={"post_id": self.p1.id})

        response = self.client.get(url, format="json")
        self.assertEqual(len(response.json()), 2)


class TestCommentUpdate(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.user2 = User.objects.create_user(
            username="testuser2", password="testuser2"
        )
        self.data = {
            "title": "test post",
            "content": "test post content",
            "tags": ["test", "tags"],
        }
        self.comment = {"content": "nice post"}

    def create_post(self):
        url = reverse("post_list_create")
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(url, data=self.data, format="json")
        return response

    def create_comments(self):
        """
        Create two post and 3 comments, 2 for first post and 1 for last
        """
        self.create_post()
        self.create_post()

        self.p1 = Post.objects.first()
        self.p2 = Post.objects.last()

        url = reverse("comment_list_create", kwargs={"post_id": self.p1.id})
        url2 = reverse("comment_list_create", kwargs={"post_id": self.p2.id})

        self.client.post(url, data=self.comment, format="json")
        self.client.post(url, data=self.comment, format="json")

        self.client.post(url2, data=self.comment, format="json")

    def test_comment_update_for_authenticated_user_returns_201(self):
        self.create_comments()
        p1 = Post.objects.first()
        c1 = p1.comment.first()

        url = reverse(
            "comment_retrieve_update_delete",
            kwargs={"post_id": p1.id, "comment_id": c1.id},
        )
        comment = self.comment.copy()
        comment["content"] = "updated"
        response = self.client.put(url, data=comment, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(p1.comment.first().content, comment["content"])

    def test_comment_update_for_unauthenticated_user_returns_403(self):
        self.create_comments()
        p1 = Post.objects.first()
        c1 = p1.comment.first()

        url = reverse(
            "comment_retrieve_update_delete",
            kwargs={"post_id": p1.id, "comment_id": c1.id},
        )
        comment = self.comment.copy()
        comment["content"] = "updated"
        self.client.logout()
        response = self.client.put(url, data=comment, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCommentDelete(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.user2 = User.objects.create_user(
            username="testuser2", password="testuser2"
        )
        self.data = {
            "title": "test post",
            "content": "test post content",
            "tags": ["test", "tags"],
        }
        self.comment = {"content": "nice post"}

    def create_post(self):
        url = reverse("post_list_create")
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(url, data=self.data, format="json")
        return response

    def create_comments(self):
        """
        Create two post and 3 comments, 2 for first post and 1 for last
        """
        self.create_post()
        self.create_post()

        self.p1 = Post.objects.first()
        self.p2 = Post.objects.last()

        url = reverse("comment_list_create", kwargs={"post_id": self.p1.id})
        url2 = reverse("comment_list_create", kwargs={"post_id": self.p2.id})

        self.client.post(url, data=self.comment, format="json")
        self.client.post(url, data=self.comment, format="json")

        self.client.post(url2, data=self.comment, format="json")

    def test_comment_delete_for_authenticated_user_returns_204(self):
        self.create_comments()
        c1 = self.p1.comment.first()
        url = reverse(
            "comment_retrieve_update_delete",
            kwargs={"post_id": self.p1.id, "comment_id": c1.id},
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comment_delete_for_unauthenticated_user_returns_403(self):
        self.create_comments()
        c1 = self.p1.comment.first()
        url = reverse(
            "comment_retrieve_update_delete",
            kwargs={"post_id": self.p1.id, "comment_id": c1.id},
        )
        self.client.logout()
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_delete_for_unauthorized_user_returns_404(self):
        self.create_comments()
        c1 = self.p1.comment.first()
        url = reverse(
            "comment_retrieve_update_delete",
            kwargs={"post_id": self.p1.id, "comment_id": c1.id},
        )
        self.client.login(username="testuser2", password="testuser2")

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
