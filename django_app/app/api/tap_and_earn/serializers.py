from datetime import timezone
import random
from django.db.models import F
from django.utils.timezone import datetime, timedelta
from rest_framework import serializers

from api.user.models import User
from api.tap_and_earn.models import TapAndEarn
from api.roulette.serializers import UserDetailSerializer


class TapAndEarnSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_details = UserDetailSerializer(source="user", read_only=True)

    class Meta:
        model = TapAndEarn
        fields = ["id", "user", "user_details", "claimed_amount", "time_last_claimed"]
        read_only_fields = ["id", "user_details", "time_last_claimed"]

    def create(self, validated_data):
        return super().create(validated_data)

    def validate(self, attrs):
        user_id = attrs["user"].pk

        user = User.objects.filter(telegram_id=user_id).first()
        if user is None:
            raise serializers.ValidationError(f"User does not exist.")

        return super().validate(attrs)
