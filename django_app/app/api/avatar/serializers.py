from rest_framework import serializers
from api.agent.models import Agent
from api.avatar.models import Avatar


class AvatarSerializer(serializers.ModelSerializer):
    agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all())

    class Meta:
        model = Avatar
        fields = [
            "id",
            "agent",
            "head",
            "skin",
            "top",
            "bottom",
            "agent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_agent(self, value):
        if self.instance is None and Avatar.objects.filter(agent=value).exists():
            raise serializers.ValidationError("This agent already has an avatar.")
        if (
            self.instance is not None
            and self.instance.agent != value
            and Avatar.objects.filter(agent=value).exists()
        ):
            raise serializers.ValidationError("This agent already has an avatar.")
        return value
