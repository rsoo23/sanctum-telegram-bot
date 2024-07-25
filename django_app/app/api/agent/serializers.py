from rest_framework import serializers
from api.agent.models import Agent
from api.user.models import User


class AgentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Agent
        fields = [
            "name",
            "user",
            "agent_id",
            # "gold",
             "is_chatting_with_user",
            "mining_rate",
            "luck",
            "energy",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            # "mining_rate",
            # "gold",
            "created_at",
            "updated_at",
        ]


class NestedAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            "agent_id",
            "name",
            # "gold",
            "luck",
             "is_chatting_with_user",
            "energy",
            "mining_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            # "gold",
            "luck",
            "energy",
            "mining_rate",
            "created_at",
            "updated_at",
        ]


class AgentInputValidation(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)
    age = serializers.IntegerField(min_value=0, required=True)
    gender = serializers.ChoiceField(
        choices=["male", "female", "nonbinary"], required=True
    )
    goal = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(max_length=500, required=True)
    telegram_id = serializers.CharField(max_length=255, required=True)
