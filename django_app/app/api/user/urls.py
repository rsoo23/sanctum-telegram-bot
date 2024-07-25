from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.user.views import UserViewSet

router = DefaultRouter()
router.register(r"user", UserViewSet)

urlpatterns = router.urls
