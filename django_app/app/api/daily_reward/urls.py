from rest_framework.routers import DefaultRouter
from .views import DailyRewardViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'daily-reward', DailyRewardViewSet, basename='daily-reward')

urlpatterns = [
    path('', include(router.urls)),
    path('daily-reward/check/<str:pk>/', DailyRewardViewSet.as_view({'get': 'check'}), name='daily-reward-check'),
]