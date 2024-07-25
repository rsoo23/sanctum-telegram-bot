from rest_framework import serializers

from api.reward_zone.models import RewardZone
from api.agent.models import Agent


class AgentIdRelatedField(serializers.RelatedField):
    def get_queryset(self):
        queryset = Agent.objects.all()
        return queryset

    def to_representation(self, value):
        return value.agent_id

    def to_internal_value(self, data):
        try:
            agent = Agent.objects.get(agent_id=data)
            return agent
        except Agent.DoesNotExist:
            raise serializers.ValidationError(
                "Agent with this agent_id does not exist."
            )


class RewardZoneSerializer(serializers.ModelSerializer):
    agent = AgentIdRelatedField(queryset=Agent.objects.all())

    class Meta:
        model = RewardZone
        fields = ["id", "agent", "amount"]
        read_only_fields = ["id", "agent"]

    def create(self, validated_data):
        return super().create(validated_data)

    def validate(self, attrs):
        agent_id = attrs["agent"].agent_id
        agent = Agent.objects.filter(agent_id=agent_id).first()
        if not agent:
            raise serializers.ValidationError(
                "Agent with this agent_id does not exist."
            )
        return attrs
