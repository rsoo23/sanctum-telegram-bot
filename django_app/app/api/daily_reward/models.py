from django.db import models

# Create your models here.
from api.user.models import User


class DailyReward(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_id = models.ForeignKey(User, on_delete=models.CASCADE, to_field='telegram_id', related_name="daily_reward")
    daily_reward = models.IntegerField()
    days_streak = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "daily_reward"

    def __str__(self):
        return f"Daily Reward for {self.id}"

    