# AVATAR
from django.db import models

# Create your models here.
from api.agent.models import Agent


class Avatar(models.Model):
    id = models.AutoField(primary_key=True)
    agent = models.OneToOneField(Agent, on_delete=models.CASCADE, related_name="avatar")
    head = models.CharField(max_length=255, default="default")
    skin = models.CharField(max_length=255, default="default")
    top = models.CharField(max_length=255, default="default")
    bottom = models.CharField(max_length=255, default="default")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "avatars"

    def __str__(self):
        return f"Avatar {self.id}"
