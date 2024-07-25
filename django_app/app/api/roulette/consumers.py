import json
from channels.consumer import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from api.roulette.models import Roulette
from api.roulette.serializers import RouletteSerializer


class RouletteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("roulette", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("roulette", self.channel_name)
        return await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        await self.send_latest_games()

    @database_sync_to_async
    def get_latest_games(self):
        latest_games = Roulette.objects.order_by("-created_at")[:10]
        return RouletteSerializer(latest_games, many=True).data

    async def send_latest_games(self):
        latest_games = await self.get_latest_games()
        await self.send(text_data=json.dumps({"games": latest_games}))

    async def new_game(self, event):
        await self.send(text_data=json.dumps(event["game"]))

    async def update_game_list(self, event):
        latest_games = await self.get_latest_games()
        await self.send(text_data=json.dumps({"games": latest_games}))
