from django.contrib.auth.models import User
from django.urls import reverse
from post.models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class TestPostCreate(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.data = {
            "title": "test post",
            "content": "test post content",
            "tags": ["test", "tags"],
        }
        self.url = reverse("post_list_create")

    def create_post(self):
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(self.url, data=self.data, format="json")

    def test_create_post_returns_201_for_authenticated_user(self):
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(self.url, data=self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], self.data["title"])

    def test_create_post_returns_403_for_unauthenticated_user(self):
        response = self.client.post(self.url, data=self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_post_returns_400(self):
        data = {
            "title": "test post",
            "content": "test post content",
        }
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestPostList(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.data = {
            "title": "test post",
            "content": "test post content",
            "tags": ["test", "tags"],
        }
        self.url = reverse("post_list_create")

    def create_post(self):
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(self.url, data=self.data, format="json")

    def test_count_post(self):
        data2 = {
            "title": "test post 2",
            "content": "test post 2 content",
            "tags": ["test", "tags"],
        }

        self.client.login(username="testuser", password="testuser")
        self.client.post(self.url, data=self.data, format="json")
        self.client.post(self.url, data=data2, format="json")

        self.assertEqual(2, Post.objects.count())

    def test_list_post(self):
        self.create_post()
        self.create_post()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_list_unpublished_post(self):
        data = {
            "title": "test post 2",
            "content": "test post 2 content",
            "tags": ["test", "tags"],
            "is_published": False,
        }
        self.create_post()
        self.client.post(self.url, data=data, format="json")
        response = self.client.get(self.url)
        self.assertEqual(len(response.json()), 1)


class TestPostRetrieve(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testuser")
        self.data = {
            "title": "test post",
            "content": "test post content",
            "tags": ["test", "tags"],
        }

    def create_post(self):
        url = reverse("post_list_create")
        self.client.login(username="testuser", password="testuser")
        response = self.client.post(url, data=self.data, format="json")
        return response

    def test_retrieve_post_returns_200_for_authenticated_user(self):
        self.create_post()
        post = Post.objects.first()
        url = reverse("post_retrieve_update_delete", kwargs={"id": post.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_post_returns_200_for_unauthenticated_user(self):
        self.client.logout()
        self.create_post()

        post = Post.objects.first()
        url = reverse("post_retrieve_update_delete", kwargs={"id": post.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_post_returns_404_for_unpublished_posts(self):
        data = {
            "title": "unpublished",
            "content": "some content",
            "tags": ["un", "published"],
            "is_published": False,
        }
        self.client.login(username="testuser", password="testuser")
        self.client.post(reverse("post_list_create"), data=data, format="json")
        post = Post.objects.first()

        url = reverse("post_retrieve_update_delete", kwargs={"id": post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestPostUpdate(APITestCase):
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

    def create_post(self, username, password):

        url = reverse("post_list_create")
        self.client.login(username=username, password=password)
        response = self.client.post(url, data=self.data, format="json")
        return response

    def test_post_update_returns_200_for_author(self):
        self.create_post("testuser", "testuser")
        self.create_post("testuser2", "testuser2")
        post1 = Post.objects.first()

        self.client.login(username="testuser", password="testuser")
        url = reverse("post_retrieve_update_delete", kwargs={"id": post1.id})
        self.data["title"] = "updated"
        response = self.client.put(url, data=self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post1 = Post.objects.first()
        self.assertEqual(post1.title, "updated")

    def test_post_update_returns_404_for_other_user(self):
        self.client.login(username="testuser2", password="testuser2")
        self.create_post("testuser", "testuser")
        self.create_post("testuser2", "testuser2")
        post1 = Post.objects.first()

        url = reverse("post_retrieve_update_delete", kwargs={"id": post1.id})
        self.data["title"] = "updated"
        response = self.client.put(url, data=self.data, format="json")

        post1 = Post.objects.first()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(post1.title, "updated")


class TestPostDelete(APITestCase):
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

    def create_post(self, username, password):

        url = reverse("post_list_create")
        self.client.login(username=username, password=password)
        response = self.client.post(url, data=self.data, format="json")
        return response

    def test_post_delete_returns_204_for_author(self):
        self.create_post("testuser", "testuser")
        post1 = Post.objects.first()

        self.client.login(username="testuser", password="testuser")
        url = reverse("post_retrieve_update_delete", kwargs={"id": post1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_delete_returns_401_for_other_user(self):
        self.create_post("testuser2", "testuser2")
        post1 = Post.objects.first()

        self.client.login(username="testuser", password="testuser")
        url = reverse("post_retrieve_update_delete", kwargs={"id": post1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.count(), 1)
