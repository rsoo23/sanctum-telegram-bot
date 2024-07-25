from rest_framework import serializers
from .models import DailyReward
from api.user.models import User
from django.utils import timezone



class DailyRewardSerializer(serializers.ModelSerializer):
    telegram_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = DailyReward
        fields = ["telegram_id", "daily_reward", "days_streak", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    @classmethod
    def get_reward_status(cls, telegram_id):
        today = timezone.now().date()

        latest_reward = DailyReward.objects.filter(telegram_id=telegram_id, created_at__date=today).order_by('-created_at').first()
        
        if latest_reward:
            return {
                "day_streak": latest_reward.days_streak,
                "claimed": True,
            }
        
        previous_reward = DailyReward.objects.filter(telegram_id=telegram_id, created_at__date__lt=today).order_by('-created_at').first()
        
        if not previous_reward or previous_reward.created_at.date() < today - timezone.timedelta(days=1):
            new_streak = 0
        else:
            new_streak = (previous_reward.days_streak + 1) % 8 
        
        return {
            "day_streak": new_streak,
            "claimed": False,
        }