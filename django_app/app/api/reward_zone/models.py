from django.db import models

from api.agent.models import Agent

# Create your models here.


class RewardZone(models.Model):
    id = models.AutoField(primary_key=True)
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="reward_zones"
    )
    amount = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reward_zones"

    def __str__(self):
        return f"RewardZone {self.id}"
