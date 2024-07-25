from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.agent.views import AgentViewSet

router = DefaultRouter()
router.register(r"agent", AgentViewSet)

urlpatterns = router.urls
