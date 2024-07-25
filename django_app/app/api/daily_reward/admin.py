from django.contrib import admin

# Register your models here.
from api.daily_reward.models import DailyReward

admin.site.register(DailyReward)