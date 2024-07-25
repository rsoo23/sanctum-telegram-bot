from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import Response
from api.referral_history.models import ReferralHistory
from api.referral_history.serializers import ReferralHistorySerializer
from sanctum.config import API_KEY

# Create your views here.


class ReferralHistoryViewSet(viewsets.ModelViewSet):
    queryset = ReferralHistory.objects.all()
    serializer_class = ReferralHistorySerializer

    @extend_schema(description="Creates a new ReferralHistory")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Completely updates the selected ReferralHistory to the new uploaded ReferralHistory"
    )
    def update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Gets the list of all ReferralHistory in the database"
    )
    def list(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().list(request, *args, **kwargs)

    @extend_schema(description="Gets the details of the selected ReferralHistory")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Partially update the selected ReferralHistory with the new information sent"
    )
    def partial_update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().partial_update(request, *args, **kwargs)

    @extend_schema(description="[Protected] Deletes the selected ReferralHistory")
    def destroy(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().destroy(request, *args, **kwargs)

    @extend_schema(description="Gets the referral history of the selected user")
    @action(detail=False, methods=["get"], url_path="user/<int:user_id>")
    def user(self, request, user_id=None):
        referred_history_list = ReferralHistory.objects.filter(referred_by=user_id)
        return Response(
            ReferralHistorySerializer(referred_history_list, many=True).data,
            status=status.HTTP_200_OK,
        )
