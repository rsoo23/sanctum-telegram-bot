from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from api.user.models import User
from api.roulette.models import Roulette

from rest_framework.test import APIClient
from datetime import datetime, timedelta

from api.referral_history.models import ReferralHistory

# client = APIClient()
# client.post("/api/user/", {"username": "test", "email": "test@test.com"}, format="json")


class TestReferralHistoryAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="random",
            email="random@example.com",
            telegram_id="512004133",
            gold=100,
        )

        self.header = {"API-key": "ABC"}

    def test_referral(self):
        url = reverse("user-list")  # Assuming you have a router and user-list URL
        data = {
            "username": "random_referral",
            "telegram_id": "12345",
            "referred_by": self.user.referral_id,
        }
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.gold, 200)
        self.assertEqual(self.user.referral_count, 1)
        self.assertEqual(response.data["referred_by"], self.user.referral_id)
        self.assertEqual(response.data["gold"], 200)
        self.assertEqual(ReferralHistory.objects.count(), 1)

        new_referral_code = response.data["referral_id"]
        data = {
            "username": "tier2_sub",
            "telegram_id": "123456",
            "referred_by": new_referral_code,
        }
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.gold, 220)
        self.assertEqual(User.objects.get(referral_id=new_referral_code).gold, 300)
        self.assertEqual(response.data["referred_by"], new_referral_code)
        self.assertEqual(response.data["gold"], 200)
        self.assertEqual(ReferralHistory.objects.count(), 3)

# test lookup now
        url = reverse("referral-history-user", args=[self.user.telegram_id])
        response = self.client.get(url, format="json")
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["referred"], "random_referral")
        self.assertEqual(response.data[1]["referred"], "Commission")


