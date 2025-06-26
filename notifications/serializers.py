from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models import User
from children.models import Child
from .models import Notification, Reward


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = User
        fields = ['avatar', 'full_name', 'email']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'username', 'avatar']  # Include the fields you want to expose


class PasswordResetSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords do not match.")
        validate_password(data['new_password'])
        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "is_read",
            "created_at",
            "related_id",
        ]



class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = [
            'reward_approval_required',
            'max_daily_reward',
            'allow_savings'
        ]