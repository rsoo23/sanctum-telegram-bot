from django.shortcuts import render

from api.reward_zone.serializers import RewardZoneSerializer
from api.reward_zone.models import RewardZone

from rest_framework.decorators import action
from django.utils.timezone import datetime, timedelta
from rest_framework import viewsets
from rest_framework.routers import Response

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import AuthenticationFailed, status
from api.agent.models import Agent
from api.user.models import User
from sanctum.config import API_KEY, BOT_TOKEN, TG_API_BASE
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

import random
import requests
# Create your views here.


class RewardZoneViewSet(viewsets.ModelViewSet):
    queryset = RewardZone.objects.all()
    serializer_class = RewardZoneSerializer

    @extend_schema(description="Creates a new RewardZone")
    def create(self, request, *args, **kwargs):
        if request.data.get("amount") is None:
            return Response(
                {"Error": "Claimed amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Completely updates the selected RewardZone to the new uploaded RewardZone"
    )
    def update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")
        if request.data.get("amount") is None:
            return Response(
                {"Error": "amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Gets the list of all RewardZone in the database"
    )
    def list(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().list(request, *args, **kwargs)

    @extend_schema(description="Gets the details of the selected RewardZone")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Partially update the selected RewardZone with the new information sent"
    )
    def partial_update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().partial_update(request, *args, **kwargs)

    @extend_schema(description="[Protected] Deletes the selected RewardZone")
    def destroy(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def mine(self, request):
        # agent_id = request.data.get("agent")
        user_id = request.data.get("user")

        if request.data.get("amount"):
            return Response(
                {"Error": "Amount is not allowed"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # agent = Agent.objects.get(agent_id=agent_id)
            # user = agent.user
            user = User.objects.get(telegram_id=user_id)
            agent_list = user.agents.all()
            agent = agent_list[0]

            cut_off_time = datetime.now().astimezone() - timedelta(hours=4)
            if user.last_logged_in is not None and user.last_logged_in < cut_off_time:
                return Response(
                    {"Error": "User have been logged off for too long."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Agent.DoesNotExist:
            return Response(
                {"Error": "Agent does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"Error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )

        gold_mined = random.randint(1, 100)
        amount = int(gold_mined * agent.mining_rate)

        mine_data = {
            "agent": agent.agent_id,
            "amount": amount,
        }

        serializer = self.get_serializer(data=mine_data)
        if serializer.is_valid():
            serializer.save()
            user.gold += amount
            user.save()
            user.refresh_from_db()
            # NOTE:keeping this incase change of mind
            # agent.gold += amount
            # agent.save()
            # agent.refresh_from_db()
            try:
                tmp_header = {"Content-Type": "application/json"}
                jsonBody = {
                    "chat_id": int(agent.user.telegram_id),
                    "text": f"Agent {agent.name} has finished mining and they have gathered {amount} godl",
                    "parse_mode": "markdown"
                }
                requests.post(TG_API_BASE + f"/bot{BOT_TOKEN}/sendMessage", json=jsonBody, headers=tmp_header)
            except requests.exceptions.RequestException:
                pass

            return_data = serializer.data
            return_data["user"] = user.telegram_id
            return Response(return_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
