from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.user.models import User

from rest_framework.test import APIClient

from api.daily_reward.models import DailyReward
from datetime import datetime, timedelta

# client = APIClient()
# client.post("/api/user/", {"username": "test", "email": "test@test.com"}, format="json")


class TestUserAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="random",
            email="random@example.com",
            telegram_id="512004133",
            gold=100,
        )
        self.daily_reward = DailyReward.objects.create(
            telegram_id = self.user,
            daily_reward = 50,
            days_streak = 4,
        )
        self.user1 = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            telegram_id=123456,
            gold=100,
        )
        self.daily_reward.created_at -= timedelta(days=1)
        self.daily_reward.save()
        self.header = {"API-key": "ABC"}

    def test_claim_streak(self):
        url = reverse("daily-reward-claim")  # Assuming you have a router and user-list URL
        data = {
            "telegram_id": "512004133",
        }
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailyReward.objects.count(), 2)
        self.assertEqual(self.user.gold, 170)
        self.assertEqual(response.data["day_streak"], self.daily_reward.days_streak + 1)

        url = reverse("daily-reward-check", args=[self.daily_reward.telegram_id.telegram_id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["day_streak"], self.daily_reward.days_streak + 1)
        self.assertEqual(response.data["claimed"], True)

    def test_claim_streak_break(self):
        self.daily_reward.created_at -= timedelta(days=2)
        self.daily_reward.save()
        self.daily_reward.refresh_from_db()
        url = reverse("daily-reward-claim")  # Assuming you have a router and user-list URL
        data = {
            "telegram_id": "512004133",
        }
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailyReward.objects.count(), 2)
        self.assertEqual(self.user.gold, 110)
        self.assertEqual(response.data["day_streak"], 0)

        url = reverse("daily-reward-check", args=[self.daily_reward.telegram_id.telegram_id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["day_streak"], 0)
        self.assertEqual(response.data["claimed"], True)

    def test_claim_already(self):
        self.daily_reward.created_at = datetime.now()
        self.daily_reward.save()
        self.daily_reward.refresh_from_db()
        url = reverse("daily-reward-claim")  # Assuming you have a router and user-list URL
        data = {
            "telegram_id": "512004133",
        }
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, { "Reward has been claimed already" })
        self.assertEqual(DailyReward.objects.count(), 1)
        self.assertEqual(self.user.gold, 100)

    def test_check(self):
        url = reverse("daily-reward-check", args=[self.daily_reward.telegram_id.telegram_id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["day_streak"], 5)
        self.assertEqual(response.data["claimed"], False)

    def test_check_user_not_found(self):
        url = reverse("daily-reward-check", args=[self.user.username])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User not found")
        


    # def test_get_agent(self):
    #     url = reverse("agent-detail", args=[self.agent.agent_id])
    #     response = self.cliAgenteAgentnt.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["agent_id"], self.agent.agent_id)
    #
