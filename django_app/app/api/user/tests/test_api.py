from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.user.models import User

from rest_framework.test import APIClient

# client = APIClient()
# client.post("/api/user/", {"username": "test", "email": "test@test.com"}, format="json")


class TestUserAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            telegram_id=123456,
            gold=100,
        )
        self.header = {"API-key": "ABC"}

    def test_create_user(self):
        url = reverse("user-list")  # Assuming you have a router and user-list URL
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "telegram_id": 654321,
            "gold": 50,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_get_user(self):
        url = reverse("user-detail", args=[self.user.telegram_id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)

    def test_status_login(self):
        url = reverse("user-status", args=[self.user.telegram_id])
        payload = {"action": "login"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User status updated successfully")

    def test_get_status(self):
        url = reverse("user-get-status")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data), 2)
        
    def test_status_logout(self):
        url = reverse("user-status", args=[self.user.telegram_id])
        payload = {"action": "logout"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User status updated successfully")

    def test_status_invalid(self):
        url = reverse("user-status", args=[self.user.telegram_id])
        payload = {"action": "none"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["Error"], "Command not recognized.")

    def test_delete_user(self):
        url = reverse("user-detail", args=[self.user.telegram_id])
        response = self.client.delete(url, format="json", headers=self.header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)
