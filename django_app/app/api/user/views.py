from django.conf import empty
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.template import context
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import Response
from api.user.models import User
from django.db.models import F, Q
from api.user.serializers import UserAgentSerializer, UserRankSerializer, UserSerializer
from datetime import date, datetime, timezone, timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import AuthenticationFailed
from api.referral_history.serializers import ReferralHistorySerializer
from api.pagination.custom_pagination import (
    LeaderboardCursorGoldPagination,
    LeaderboardCursorReferralPagination,
)
from api.agent.models import Agent
from sanctum.config import API_KEY

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "telegram_id"

    @extend_schema(
        description="Creates a new user. If new user is referred, both new user and referring user will get a bonus 100 gold. If user is created before 17 June, they will also get an additional 200 gold."
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_user = serializer.save()

        current_date = date.today()
        if current_date < date(current_date.year, 6, 17):
            created_user.gold = F("gold") + 200
            created_user.save()
            created_user.refresh_from_db()

        # self.perform_create(serializer)
        if created_user.referred_by:
            try:
                referring_user = User.objects.get(referral_id=created_user.referred_by)
                referring_user.gold = F("gold") + 100
                referring_user.referral_count = F("referral_count") + 1
                referring_user.save()
                referring_user.refresh_from_db()

                created_user.gold = F("gold") + 100
                created_user.save()
                created_user.refresh_from_db()

                referral_data = {
                    "referred_by": referring_user.telegram_id,
                    "amount": 100,
                    "referred": created_user.username,
                }
                referral_serializer = ReferralHistorySerializer(data=referral_data)
                referral_serializer.is_valid(raise_exception=True)
                referral_serializer.save()

                if referring_user.referred_by:
                    referral_t2_user = User.objects.get(
                        referral_id=referring_user.referred_by
                    )
                    referral_t2_user.gold = F("gold") + 20
                    referral_t2_user.save()
                    referral_t2_user.refresh_from_db()
                    referral_t2 = {
                        "referred_by": referral_t2_user.telegram_id,
                        "amount": 5,
                        "referred": "Commission",
                    }
                    referral_t2_serializer = ReferralHistorySerializer(data=referral_t2)
                    referral_t2_serializer.is_valid(raise_exception=True)
                    referral_t2_serializer.save()

            except User.DoesNotExist:
                created_user.referred_by = None
                created_user.save()
                # raise ValidationError("Referring user does not exist.")
        # TODO: send a API request to sancums backend to get agentID using their telegramID
        #       save it to db
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return super().create(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Completely updates the selected user to the new uploaded user"
    )
    def update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @extend_schema(description="[Protected] Gets the list of all users in the database")
    def list(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().list(request, *args, **kwargs)

    @extend_schema(description="Gets the details of the selected user")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Partially update the selected user with the new information sent"
    )
    def partial_update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().partial_update(request, *args, **kwargs)

    @extend_schema(description="[Protected] Deletes the selected user")
    def destroy(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="returns list of users ranked based on type",
        parameters=[
            OpenApiParameter(
                name="type",
                description="type of the request, must be gold or referral",
                required=True,
                type=OpenApiTypes.STR,
                enum=["gold", "referral"],
            ),
        ],
        responses={200: UserRankSerializer},
    )
    @action(detail=True, methods=["get"], url_path="leaderboard")
    def leaderboard(self, request, telegram_id=None):
        type_param = request.query_params.get("type")

        if type_param == "gold":
            users = User.objects.order_by("-gold", "-created_at")[:10]
        elif type_param == "referral":
            users = User.objects.order_by("-referral_count", "-created_at")[:10]
        else:
            return Response(
                {"error": "Invalid type parameter"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = self.get_object()
        users_top10 = any(user.telegram_id == telegram_id for user in users)

        if not users_top10:
            users = list(users)
            users.append(user)

        serializer = UserRankSerializer(users, many=True, context={"request": request})
        serializer = UserRankSerializer(users, many=True, context={"request": request})
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        description="returns list of users ranked based on type (pagination), next link/page will be returned in the response",
        parameters=[
            OpenApiParameter(
                name="type",
                description="type of the request, must be gold or referral",
                required=True,
                type=OpenApiTypes.STR,
                enum=["gold", "referral"],
            ),
            OpenApiParameter(
                name="cursor",
                description="Cursor indicating the position to start fetching results.",
                required=False,
                type=OpenApiTypes.UUID,  # Example type, adjust as per your needs
            ),
        ],
    )
    @action(detail=True, methods=["get"], url_path="leaderboard_page")
    def leaderboard_page(self, request, telegram_id=None):
        type_param = request.query_params.get("type", "gold")
        user = self.get_object()

        if type_param not in ["gold", "referral"]:
            return Response(
                {"error": "Invalid type parameter"}, status=status.HTTP_400_BAD_REQUEST
            )

        if type_param == "referral":
            paginator = LeaderboardCursorReferralPagination()
        else:
            paginator = LeaderboardCursorGoldPagination()

        paginated_users = paginator.paginate_queryset(self.queryset, request)

        list_serializer = UserRankSerializer(
            paginated_users, many=True, context={"request": request}
        )

        response = paginator.get_paginated_response(list_serializer.data)
        if paginated_users is not None:
            users_top10 = any(
                user.telegram_id == telegram_id for user in paginated_users
            )

        if paginated_users is not None and not any(
            user.telegram_id == telegram_id for user in paginated_users
        ):
            user_serializer = UserRankSerializer(user, context={"request": request})
            response.data["current_user"] = user_serializer.data

        return response

    @extend_schema(
        request=None,
        responses={
            200: 'User status updated successfully',
            400: 'Command not recognized',
            404: 'User not found',
            500: 'Internal server error'
        },
        description="Update user status to login or logout based on the action provided.",
        parameters=[
            {
                'name': 'action',
                'required': True,
                'in': 'body',
                'description': 'The action to perform (login/logout)',
                'schema': {
                    'type': 'string',
                    'enum': ['login', 'logout']
                }
            }
        ]
    )
    @action(detail=True, methods=["post"], url_path="status")
    def status(self, request, telegram_id=None):
        try:
            user = self.get_object()
            if request.data.get("action") == "login":
                user.last_logged_in = None
            elif request.data.get("action") == "logout":
                user.last_logged_in = datetime.now()
            else:
                return Response(
                    {"Error": "Command not recognized."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.save()
            return Response(
                {"message": "User status updated successfully"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        responses=UserAgentSerializer(many=True),
        description="Retrieve agents where the user's last login time is null or within the last 4 hours.",
    )
    @action(detail=False, methods=["get"], url_path="get_status")
    def get_status(self, request):
        time_threshold = datetime.now() - timedelta(hours=4)

        # Query users where last_logged_in is null or within the last 4 hours
        # users = User.objects.filter(
        #     models.Q(last_logged_in__isnull=True)
        #     | models.Q(last_logged_in__gte=time_threshold)
        # )
        agents = Agent.objects.filter(
            Q(user__last_logged_in__isnull=True)
            # | Q(user__last_logged_in__lte=time_threshold)
            | Q(user__last_logged_in__gte=time_threshold)
        )
        # print("-------------------------------")
        # print(agents)

        # Serialize the queryset or return as needed
        serializer = UserAgentSerializer(agents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# TODO: integrate last login time
