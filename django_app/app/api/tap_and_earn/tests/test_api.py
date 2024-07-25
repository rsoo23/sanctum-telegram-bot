from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from api.user.models import User
from api.roulette.models import Roulette

from rest_framework.test import APIClient
from datetime import datetime, timedelta

from api.tap_and_earn.models import TapAndEarn

# client = APIClient()
# client.post("/api/user/", {"username": "test", "email": "test@test.com"}, format="json")


class TestTapAndEarnAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="random",
            email="random@example.com",
            telegram_id="512004133",
            gold=100,
        )
        self.claim = TapAndEarn.objects.create(
            user = self.user,
            claimed_amount = 69,
        )

        self.header = {"API-key": "ABC"}

    def test_tap_claim(self):
        url = reverse("tap_and_earn-claim")  # Assuming you have a router and user-list URL
        data = {
            "user": "512004133",
        }
        self.claim.time_last_claimed = datetime.now() - timedelta(days=2)
        self.claim.save()
        self.claim.refresh_from_db()
        response = self.client.post(url, data, format="json")
        self.user.refresh_from_db()
        self.assertGreater(self.user.gold, 100)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"Error": "You can only claim once per hour."})

        response = self.client.post(url, {"user": "fksdjfkls"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"Error": "User does not exist."})


    def test_lookup(self):
        url = reverse("tap_and_earn-lookup")  # Assuming you have a router and user-list URL
        query_param  = f"?user_id={self.user.telegram_id}"
        query_url = f"{url}{query_param}"

        response = self.client.get(query_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.telegram_id)
        self.assertEqual(response.data["claimed_amount"], self.claim.claimed_amount)

        query_param  = f"?user_id=fjdsklaf"
        query_url = f"{url}{query_param}"
        response = self.client.get(query_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, { "Not Found" })
