from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from api.user.models import User
from api.agent.models import Agent
from api.reward_zone.models import RewardZone

from rest_framework.test import APIClient
from datetime import datetime, timedelta

from api.tap_and_earn.models import TapAndEarn

# client = APIClient()
# client.post("/api/user/", {"username": "test", "email": "test@test.com"}, format="json")


class TestRewardZoneAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="random",
            email="random@example.com",
            telegram_id="512004133",
            gold=100,
        )

        self.agent = Agent.objects.create(
            name="John",
            user=self.user,
            agent_id="668e28ed50a4ca041b28023d",
            is_chatting_with_user=True,
            mining_rate=1.0,
            luck=69,
            energy=240,
        )

        self.header = {"API-key": "ABC"}

    def test_mine(self):
        self.user.last_logged_in = None
        self.user.save()
        self.user.refresh_from_db()
        url = reverse("reward_zone-mine")  # Assuming you have a router and user-list URL
        data = {
            "user": "512004133",
        }
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.data["agent"], self.agent.agent_id)
        self.assertEqual(response.data["user"], self.user.telegram_id)
        self.assertEqual(self.user.gold, response.data["amount"] + 100)
        self.assertEqual(RewardZone.objects.count(), 1)
