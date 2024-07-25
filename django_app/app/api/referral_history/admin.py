from django.contrib import admin

# Register your models here.
from api.referral_history.models import ReferralHistory

admin.site.register(ReferralHistory)
