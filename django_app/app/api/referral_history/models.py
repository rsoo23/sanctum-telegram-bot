from django.db import models

from api.user.models import User

# Create your models here.


class ReferralHistory(models.Model):
    id = models.AutoField(primary_key=True)
    referred_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="referrals"
    )
    amount = models.IntegerField()
    referred = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "referral_history"

    def __str__(self):
        return super().__str__()
