# USER
from django.db import models
from django.db.models.fields import uuid
from datetime import datetime, timedelta
import hashlib

# Create your models here.
# null is for db, blank is serializer/application layer


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    telegram_id = models.CharField(primary_key=True, unique=True)
    gold = models.IntegerField(default=100)
    referral_id = models.CharField(blank=True, max_length=8)
    referred_by = models.CharField(null=True, blank=True, max_length=8)
    referral_count = models.IntegerField(default=0, blank=True)
    last_logged_in = models.DateTimeField(
        default=datetime(2024, 7, 5, 22, 25, 29, 466837), null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"User {self.telegram_id}: {self.username}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.referral_id:
            self.referral_id = self.generate_referral_id()
        return super().save(force_insert, force_update, using, update_fields)

    def generate_referral_id(self):
        while True:
            data = f"{self.telegram_id}{str(uuid.uuid4())}"
            referral_id = hashlib.sha256(data.encode()).hexdigest()[:8].upper()
            if not User.objects.filter(referral_id=referral_id).exists():
                return referral_id
