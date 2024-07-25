from asgiref.sync import async_to_sync
from channels.consumer import get_channel_layer
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.routers import Response
from api.roulette.models import Roulette
from api.roulette.serializers import RouletteSerializer
from api.user.models import User
from django.db.models import F
from drf_spectacular.utils import extend_schema
from sanctum.config import API_KEY
from rest_framework.exceptions import AuthenticationFailed


# Create your views here.
class RouletteViewSet(viewsets.ModelViewSet):
    queryset = Roulette.objects.all()
    serializer_class = RouletteSerializer

    @extend_schema(
        description="[Protected] Creates a new roulette game (For admin use, for api calls use roulette/play)"
    )
    def create(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        created_roulette = serializer.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "roulette",
            {"type": "send_game", "game": RouletteSerializer(created_roulette).data},
        )
        return Response(
            RouletteSerializer(created_roulette).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        description="[Protected] Completely updates the selected roulette game to the new uploaded roulette game"
    )
    def update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        response = super().update(request, *args, **kwargs)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "roulette",
            {"type": "update_game_list"},
        )
        return response

    @extend_schema(
        description="[Protected] Gets the list of all roulette games in the database"
    )
    def list(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().list(request, *args, **kwargs)

    @extend_schema(description="Gets the details of the selected roulette game")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Partially update the selected roulette game with the new information sent"
    )
    def partial_update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().partial_update(request, *args, **kwargs)

    @extend_schema(description="[Protected] Deletes the selected roulette game")
    def destroy(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        instance = self.get_object()
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user = instance.user
        user.gold -= instance.outcome
        user.save()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="Creates a new roulette game entry, winning will double the bet amount, whereas losing will just lose the amount bet. (Will automatically updates user's gold as well)"
    )
    @action(detail=False, methods=["post"])
    def play(self, request):
        import random

        result = random.choice(["win", "lose"])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bet = serializer.validated_data["bet"]
        outcome = bet if result == "win" else -bet
        created_roulette = serializer.save(outcome=outcome)

        player = created_roulette.user
        player.gold = F("gold") + outcome
        player.save()
        player.refresh_from_db()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "roulette",
            {"type": "new_game", "game": RouletteSerializer(created_roulette).data},
        )
        return Response(
            RouletteSerializer(created_roulette).data, status=status.HTTP_201_CREATED
        )
