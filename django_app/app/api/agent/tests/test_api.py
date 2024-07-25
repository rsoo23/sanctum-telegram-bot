from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.agent.models import Agent
from api.user.models import User

from rest_framework.test import APIClient

# client = APIClient()
# client.post("/api/user/", {"username": "test", "email": "test@test.com"}, format="json")


class TestAgentAPITestCase(APITestCase):

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
        self.user1 = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            telegram_id=123456,
            gold=100,
        )
        self.header = {"API-key": "ABC"}

    def test_create_agent(self):
        url = reverse("agent-list")  # Assuming you have a router and user-list URL
        data = {
            "username": "tesqt3",
            "email": "mengo3@test.com",
            "telegram_id": "123456",
            "name": "10",
            "age": 19,
            "gender": "male",
            "goal": "to be the best",
            "description": "test",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agent.objects.count(), 2)

    def test_get_agent(self):
        url = reverse("agent-detail", args=[self.agent.agent_id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["agent_id"], self.agent.agent_id)

