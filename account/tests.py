from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .serializers import UserCreateSerializer


class TestUserCreateSerializer(APITestCase):
    def setUp(self):
        self.data = {
            "username": "testuser",
            "email": "test@user.com",
            "password": "testuserpassword",
            "password2": "testuserpassword",
        }
        self.url = reverse("user-create")

    def test_create_user(self):
        response = self.client.post(self.url, data=self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_user_create_does_not_return_password_field(self):
        response = self.client.post(self.url, data=self.data, format="json")
        self.assertNotContains(
            response,
            "password",
            status_code=status.HTTP_201_CREATED,
        )

    def test_user_create_checks_password(self):
        data = self.data.copy()
        data["password2"] = "notsamepassword"

        response = self.client.post(self.url, data=data, format="json")
        self.assertContains(
            response,
            "Passwords do not match",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(User.objects.count(), 0)

    def test_user_create_does_not_create_user_with_same_username(self):
        response = self.client.post(self.url, data=self.data, format="json")
        response = self.client.post(self.url, data=self.data, format="json")
        self.assertContains(
            response,
            "A user with that username already exists.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(User.objects.count(), 1)

    def test_user_create_does_not_create_user_with_same_email(self):
        data2 = self.data.copy()
        data2["username"] = "testuser2"
        response = self.client.post(self.url, data=self.data, format="json")
        response = self.client.post(self.url, data=self.data, format="json")
        self.assertContains(
            response,
            "A user with that email already exists.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(User.objects.count(), 1)
