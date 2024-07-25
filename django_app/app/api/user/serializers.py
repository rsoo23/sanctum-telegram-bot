from django.db.models import F, Q
from django.db.models.query import Cast
from rest_framework import request, serializers
from rest_framework.fields import IntegerField
from api.agent.serializers import NestedAgentSerializer
from api.roulette.serializers import RouletteSerializer
from api.user.models import User
from api.agent.models import Agent


class UserSerializer(serializers.ModelSerializer):
    agents = NestedAgentSerializer(many=True, required=False)
    roulettes = RouletteSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "telegram_id",
            "referral_id",
            "username",
            "gold",
            "roulettes",
            "referred_by",
            "referral_count",
            "agents",
            "email",
            "created_at",
            "last_logged_in",
        ]
        read_only_fields = ["referral_count", "created_at", "updated_at"]

    def get_roulettes(self, obj):
        roulettes = obj.roulette_set.order_by("-created_at")[:10]
        return RouletteSerializer(roulettes, many=True).data

    def create(self, validated_data):
        agents_data = validated_data.pop("agents", [])
        user = User.objects.create(**validated_data)
        for agent_data in agents_data:
            Agent.objects.create(user=user, **agent_data)
        return user

    def update(self, instance, validated_data):
        agents_data = validated_data.pop("agents", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if agents_data:
            if not self.partial:
                instance.agents.all().delete()

            for agent in agents_data:
                agent_id = agent.get("id")
                if agent_id:
                    agent = Agent.objects.get(id=agent_id, user=instance)
                    for attr, value in agent.items():
                        setattr(agent, attr, value)
                    agent.save()
                else:
                    Agent.objects.create(user=instance, **agent)
        return instance


class UserRankSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["telegram_id", "username", "gold", "referral_count", "rank"]
        read_only_fields = ["telegram_id", "username", "gold", "referral_count", "rank"]

    def get_rank(self, obj):
        request = self.context.get("request")
        rank_by = request.query_params.get("type") if request else "gold"
        if rank_by == "referral":
            rank_by = "referral_count"
        else:
            rank_by = "gold"

        filter_kwargs = {f"{rank_by}__gt": getattr(obj, rank_by)}
        ordered_users = User.objects.order_by(F(rank_by).desc(), "-created_at")
        for idx, user in enumerate(ordered_users):
            if user.telegram_id == obj.telegram_id:
                return idx + 1


class UserAgentSerializer(serializers.ModelSerializer):
    # Define fields from User model
    telegram_id = serializers.CharField(source="user.telegram_id")
    last_logged_in = serializers.DateTimeField(source="user.last_logged_in")

    # Define fields from Agent model
    agent_id = serializers.CharField()

    class Meta:
        model = Agent
        fields = ["telegram_id", "last_logged_in", "agent_id"]
