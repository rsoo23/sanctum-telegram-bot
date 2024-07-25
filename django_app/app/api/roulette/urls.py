from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.roulette.views import RouletteViewSet
from api.roulette.consumers import RouletteConsumer

router = DefaultRouter()
router.register(r"roulette", RouletteViewSet)

websocket_urlpatterns = [
    path("ws/roulette/", RouletteConsumer.as_asgi()),
]

urlpatterns = [
    path("", include(router.urls)),
]
