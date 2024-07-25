from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.avatar.views import AvatarViewSet

router = DefaultRouter()
router.register(r"avatar", AvatarViewSet)

urlpatterns = router.urls
