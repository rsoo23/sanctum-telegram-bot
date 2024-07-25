from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from api.user.models import User
from api.roulette.models import Roulette

from rest_framework.test import APIClient

# client = APIClient()
# client.post("/api/user/", {"username": "test", "email": "test@test.com"}, format="json")


class TestRouletteAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="random",
            email="random@example.com",
            telegram_id="512004133",
            gold=100,
        )

        self.header = {"API-key": "ABC"}

    def test_play_roulette(self):
        url = reverse("roulette-play")  # Assuming you have a router and user-list URL
        data = {
            "user": "512004133",
            "bet": 100,
        }
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        if response.data["outcome"] >= 100:
            self.assertEqual(self.user.gold , 200)
        else:
            self.assertEqual(self.user.gold , 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Roulette.objects.count(), 1)
        data["bet"] += 1000
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["bet"][0], ErrorDetail(string="Insufficient GODL to place this bet.", code='invalid'))

    def test_play_invalid_user(self):
        url = reverse("roulette-play")  # Assuming you have a router and user-list URL
        data = {
            "user": "fkjsdkalf",
            "bet": 100,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "user": "512004133",
            "bet": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["bet"][0], ErrorDetail(string="The minimum bet should be 10.", code='invalid'))

        
    # def test_get_agent(self):
    #     url = reverse("agent-detail", args=[self.agent.agent_id])
    #     response = self.client.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["agent_id"], self.agent.agent_id)

