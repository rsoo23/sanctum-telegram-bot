from rest_framework.response import Response
from rest_framework import status
from .models import DailyReward
from .serializers import DailyRewardSerializer
from api.user.models import User
from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import action
from rest_framework import viewsets, status
from sanctum.config import API_KEY
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.utils import extend_schema



class DailyRewardViewSet(viewsets.ModelViewSet):
    queryset = DailyReward.objects.all()
    serializer_class = DailyRewardSerializer


    @extend_schema(description="[Protected] Can claim reward multiple times directly in the same day")
    def create(self, request):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")
        
        telegram_id = request.data.get('telegram_id')
        
        if not telegram_id:
            return Response({"error": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(telegram_id=telegram_id)
                
                today = timezone.now().date()
                latest_reward = DailyReward.objects.filter(telegram_id=telegram_id).order_by('-created_at').first()
                
                if not latest_reward or (today - latest_reward.created_at.date()).days > 1:
                    new_streak = 0
                else:
                    new_streak = latest_reward.days_streak
                    if new_streak == 7:
                        new_streak = 0
                    else:
                        new_streak += 1
                
                daily_reward_amount = [10, 20, 30, 50, 60, 70, 100, 120][new_streak]
                
                daily_reward_data = {
                    'telegram_id': telegram_id,
                    'daily_reward': daily_reward_amount,
                    'days_streak': new_streak,
                }
                
                serializer = self.get_serializer(data=daily_reward_data)
                if serializer.is_valid():
                    serializer.save()
                    user.gold += daily_reward_amount
                    user.save()
                    
                    return Response({
                        "day_streak": new_streak,
                        "claimed": True
                    }, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


    @extend_schema(description="[Protected] List all data in the daily reward table")
    def list(self, request):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        users = DailyReward.objects.all()
        serializer = DailyRewardSerializer(users, many=True)
        return Response(serializer.data)
    

    @extend_schema(description="[Protected] Delete most recent data in the table based on telegram_id")
    def destroy(self, request, pk=None):
        api_key = request.headers.get("API-key")
        if api_key != API_KEY:
            raise AuthenticationFailed("Invalid API key")

        try:
            most_recent_reward = DailyReward.objects.filter(telegram_id=pk).order_by('-created_at').first()
            
            if not most_recent_reward:
                return Response({"error": "No DailyReward found for this telegram_id"}, status=status.HTTP_404_NOT_FOUND)
            
            deleted_date = most_recent_reward.created_at
            most_recent_reward.delete()
            
            return Response({
                "message": f"Successfully deleted the most recent DailyReward for telegram_id {pk}",
                "deleted_date": deleted_date
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @extend_schema(description="Check user can claim or not")    
    @action(detail=False, methods=["get"])
    def check(self, request, pk=None):
        telegram_id = pk
        
        if not telegram_id:
            return Response({"error": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(telegram_id=telegram_id)
            reward_status = DailyRewardSerializer.get_reward_status(telegram_id)
            return Response(reward_status, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
    @extend_schema(description="User claim daily reward")   
    @action(detail=False, methods=["post"])
    def claim(self, request):
        telegram_id = request.data.get('telegram_id')
        
        if not telegram_id:
            return Response({"error": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                user = User.objects.select_for_update().get(telegram_id=telegram_id)
                
                reward_status = DailyRewardSerializer.get_reward_status(telegram_id)
                
                if reward_status['claimed']:
                    return Response({
                        "Reward has been claimed already"
                    }, status=status.HTTP_200_OK)
                
                new_streak = reward_status['day_streak']
                daily_reward_amount = [10, 20, 30, 50, 60, 70, 100, 120][new_streak]
                
                daily_reward_data = {
                    'telegram_id': telegram_id,
                    'daily_reward': daily_reward_amount,
                    'days_streak': new_streak,
                }
                
                serializer = self.get_serializer(data=daily_reward_data)
                if serializer.is_valid():
                    serializer.save()
                    user.gold += daily_reward_amount
                    user.save()
                    
                    return Response({
                        "day_streak": new_streak,
                        "claimed": True
                    }, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

 
