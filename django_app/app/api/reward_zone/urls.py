from django.urls import path, include
from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter
from api.reward_zone.views import RewardZoneViewSet

router = DefaultRouter()
router.register(r"reward_zone", RewardZoneViewSet, basename="reward_zone")

urlpatterns = router.urls
