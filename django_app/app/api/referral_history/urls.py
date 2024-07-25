from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.referral_history.views import ReferralHistoryViewSet

router = DefaultRouter()
router.register(r"referral_history", ReferralHistoryViewSet)

urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
    path(
        "referral_history/user/<int:user_id>/",
        ReferralHistoryViewSet.as_view({"get": "user"}),
        name="referral-history-user",
    ),
]
