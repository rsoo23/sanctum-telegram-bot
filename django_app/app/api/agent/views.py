from django.shortcuts import render
from django.views.generic import detail
from rest_framework import viewsets, status
from api.agent.models import Agent
from api.agent.serializers import AgentSerializer, AgentInputValidation
from api.user.models import User
from sanctum.config import API_KEY, X_API_KEY, X_BASE_URL
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    action,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, ValidationError
import requests
import random
from drf_spectacular.utils import extend_schema

# Create your views here.


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    lookup_field = "agent_id"

    @extend_schema(description="Creates a new Agent", request=AgentInputValidation)
    def create(self, request, *args, **kwargs):
        input_serializer = AgentInputValidation(data=request.data)
        user_id = request.data.get("telegram_id")
        if not user_id:
            return Response(
                {"Error": "Telegram_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(telegram_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"Error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )
        agent = Agent.objects.filter(user=user.telegram_id).first()
        if agent is not None:
            return Response(
                {"Error": "Agent already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        # REQUEST
        headers = {"X-API-KEY": X_API_KEY, "Content-Type": "application/json"}
        json_body = {
            "name": request.data.get("name"),
            "age": request.data.get("age"),
            "gender": request.data.get("gender"),
            "goal": request.data.get("goal"),
            "description": request.data.get("description"),
        }

        input_serializer.is_valid(raise_exception=True)
        try:
            agent_data = {
                "name": request.data.get("name"),
                "user": request.data.get("telegram_id"),
                "agent_id": "123456789",
                "mining_rate": random.uniform(0.7, 1.3),
                "luck": random.randint(0, 100),
                "energy": 240,
            }
            agent_serializer = AgentSerializer(data=agent_data)
            agent_serializer.is_valid(raise_exception=True)
            response = requests.post(
                X_BASE_URL + "/agents", json=json_body, headers=headers
            )
            if response.status_code >= 200 and response.status_code <= 226:
                JSONdata = response.json()
                agent_serializer.validated_data["agent_id"] = JSONdata["data"]["id"]
                if agent_serializer.is_valid(raise_exception=True):
                    agent_serializer.save()
                    return Response(
                        {
                            "detail": "Agent successfully created",
                            "data": agent_serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"detail": "Agent failed to be verified"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(
                {
                    "detail": "Sanctum api returned status code: "
                    + str(response.status_code)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except requests.exceptions.RequestException:
            return Response(
                {"detail": "Sanctum api endpoint was unreachable"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeyError:
            return Response(
                {"detail": "KeyError occured"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="[Protected] Completely updates the selected Agent to the new uploaded Agent"
    )
    def update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().update(request, *args, **kwargs)

    @extend_schema(description="[Protected] Gets the list of all Agent in the database")
    def list(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().list(request, *args, **kwargs)

    @extend_schema(description="Gets the details of the selected Agent")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="[Protected] Partially update the selected Agent with the new information sent"
    )
    def partial_update(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().partial_update(request, *args, **kwargs)

    @extend_schema(description="[Protected] Deletes the selected Agent")
    def destroy(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="lookup")
    def lookup(self, request):
        type_param = request.query_params.get("user_id")
        if type_param is None:
            return Response(
                {"Error": "User_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        agent = Agent.objects.filter(user=type_param).first()
        if agent is None:
            return Response({"data": None}, status=status.HTTP_200_OK)
        else:
            try:
                response = requests.get(
                    X_BASE_URL + "/agents/", headers={"X-API-KEY": X_API_KEY}
                )
                if response.status_code >= 200 and response.status_code <= 226:
                    JSONdata = response.json()
                    r_val = None

                    for i in JSONdata["agents"]:
                        if i["id"] == agent.agent_id:
                            r_val = i
                            break

                    if r_val is not None:
                        return Response({"data": r_val}, status=status.HTTP_200_OK)
                    else:
                        return Response({"data": None}, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException:
                return Response(
                    {"detail": "Sanctum api endpoint was unreachable"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(detail=False, methods=["post"], url_path="chatting_with_agent")
    def chatting_with_agent(self, request, *args, **kwargs):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        errors = {}
        agent = request.data.get("agent_id")
        is_chatting = request.data.get("is_chatting")
        if not agent:
            errors["agent_id"] = "field required"
        if not is_chatting:
            errors["is_chatting"] = "field required"
        if len(errors) >= 1:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            agentObj = Agent.objects.get(agent_id=agent)
        except Agent.DoesNotExist:
            return Response({"detail": "Error agent not found"}, status=status.HTTP_404_NOT_FOUND)

        agentObj.is_chatting_with_user = is_chatting
        agentObj.save()
        return Response({"detail": "successful"}, status=status.HTTP_200_OK)



    @action(detail=False, methods=["get"], url_path="agent_id")
    def agent_id(self, request):
        type_param = request.query_params.get("agent_id")
        if type_param is None:
            return Response(
                {"Error": "agent_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            agent = Agent.objects.get(agent_id=type_param)
            agent_serializer = AgentSerializer(agent)
            return Response(agent_serializer.data, status=status.HTTP_200_OK)
        except Agent.DoesNotExist:
            return Response(
                {"Error": "Agent does not exists"},
                status=HTTP_400_BAD_REQUEST
            )

