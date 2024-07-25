# ROULETTE
from django.db import models

# Create your models here.

from api.user.models import User


class Roulette(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roulettes")
    outcome = models.IntegerField(blank=True)
    bet = models.IntegerField(default=10)

    class Meta:
        db_table = "roulettes"

    def __str__(self):
        return f"Roulette {self.id}"
