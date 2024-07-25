from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.tap_and_earn.views import TapAndEarnViewSet

router = DefaultRouter()
router.register(r"tap_and_earn", TapAndEarnViewSet, basename="tap_and_earn")

urlpatterns = router.urls
