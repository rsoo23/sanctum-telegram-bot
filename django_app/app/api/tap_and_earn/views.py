from datetime import timedelta
import random
from django.shortcuts import render

from rest_framework.decorators import action
from django.utils.timezone import datetime, timedelta
from rest_framework import viewsets
from rest_framework.routers import Response

from api.tap_and_earn.models import TapAndEarn
from api.tap_and_earn.serializers import TapAndEarnSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import AuthenticationFailed, status
from api.user.models import User
from sanctum.config import API_KEY
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

# Create your views here.
# import logging
# logger = logging.getLogger(__name__)


class TapAndEarnViewSet(viewsets.ModelViewSet):
    queryset = TapAndEarn.objects.all()
    serializer_class = TapAndEarnSerializer

    @extend_schema(description="Creates a new TapAndEarn")
    def create(self, request, *args, **kwargs):
        if request.data.get("claimed_amount") is None:
            return Response(
                {"Error": "Claimed amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Completely updates the selected TapAndEarn to the new uploaded TapAndEarn"
    )
    def update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")
        if request.data.get("claimed_amount") is None:
            return Response(
                {"Error": "claimed_amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Gets the list of all TapAndEarn in the database"
    )
    def list(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().list(request, *args, **kwargs)

    @extend_schema(description="Gets the details of the selected TapAndEarn")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Partially update the selected TapAndEarn with the new information sent"
    )
    def partial_update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().partial_update(request, *args, **kwargs)

    @extend_schema(description="[Protected] Deletes the selected TapAndEarn")
    def destroy(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="returns the latest claimed entry (based on user_id)",
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="id/primary key of user",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: TapAndEarnSerializer},
    )
    @action(detail=False, methods=["get"], url_path="lookup")
    def lookup(self, request):
        type_param = request.query_params.get("user_id")
        if type_param is None:
            return Response(
                {"Error": "User_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        latest_claim = (
            TapAndEarn.objects.filter(user_id=type_param)
            .order_by("-time_last_claimed")
            .first()
        )
        if latest_claim is None:
            return Response({"Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TapAndEarnSerializer(latest_claim)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="claims gold for user with user_id, only after a certain amount since last claimed"
    )
    @action(detail=False, methods=["post"])
    def claim(self, request):
        user_id = request.data.get("user")
        claimed_amount = request.data.get("claimed_amount")
        if claimed_amount:
            return Response(
                {"Error": "Claimed amount is not allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user_id:
            return Response(
                {"Error": "User is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(telegram_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"Error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )
        last_tap = (
            TapAndEarn.objects.filter(user=user).order_by("-time_last_claimed").first()
        )
        now = datetime.now()
        if last_tap is not None and (
            now.astimezone() - last_tap.time_last_claimed < timedelta(hours=1)
        ):
            return Response(
                {"Error": "You can only claim once per hour."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        claimed_amount = random.randint(50, 80)

        claim_data = {
            "user": user.telegram_id,
            "claimed_amount": claimed_amount,
        }
        serializer = self.get_serializer(data=claim_data)
        if serializer.is_valid():
            serializer.save()
            user.gold += claimed_amount
            user.save()
            user.refresh_from_db()
            return_data = serializer.data
            return_data["user_details"]["gold"] = user.gold
            return Response(return_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
