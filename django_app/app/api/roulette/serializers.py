from rest_framework import serializers

from api.user.models import User
from api.roulette.models import Roulette


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "gold"]


class RouletteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_details = UserDetailSerializer(source="user", read_only=True)

    class Meta:
        model = Roulette
        fields = ["id", "user", "user_details", "bet", "outcome", "created_at"]
        read_only_fields = ["id", "user_details", "outcome", "created_at"]

    def create(self, validated_data):
        return super().create(validated_data)

    def validate_bet(self, value):
        if value < 10:
            raise serializers.ValidationError("The minimum bet should be 10.")
        user_id = self.initial_data.get("user")
        if not user_id:
            raise serializers.ValidationError("User must be provided.")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        if user.gold < value:
            raise serializers.ValidationError("Insufficient GODL to place this bet.")
        return value
