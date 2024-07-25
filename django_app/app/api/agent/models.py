# AGENT
from django.db import models

# Create your models here.

from api.user.models import User


class Agent(models.Model):
    id = models.AutoField(primary_key=True)
    agent_id = models.CharField(max_length=255, default="empty")
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agents")
    is_chatting_with_user = models.BooleanField(default=False)
    # gold = models.IntegerField(default=0)
    mining_rate = models.FloatField(blank=True)
    luck = models.IntegerField(blank=True)
    energy = models.IntegerField(blank=True, default=240)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "agents"

    def __str__(self):
        return f"Agent {self.id}: {self.name}"
