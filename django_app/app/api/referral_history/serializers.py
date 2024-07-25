from rest_framework import serializers
from api.referral_history.models import ReferralHistory
from api.user.models import User


class ReferralHistorySerializer(serializers.ModelSerializer):
    referred_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ReferralHistory
        fields = ["id", "referred_by", "amount", "referred", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
