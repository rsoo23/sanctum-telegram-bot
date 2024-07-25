from django.db import models

# Create your models here.

from api.user.models import User


class TapAndEarn(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tap_and_earns"
    )
    claimed_amount = models.IntegerField(blank=True)
    time_last_claimed = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        db_table = "tap_and_earn"

    def __str__(self):
        return f"TapAndEarn {self.id}"
