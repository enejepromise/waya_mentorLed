
from rest_framework import serializers
from .models import Goal, GoalTransaction
from decimal import Decimal

class GoalTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTransaction
        fields = ['id', 'goal', 'amount', 'transaction_date']
        read_only_fields = ['id', 'transaction_date']

class GoalSerializer(serializers.ModelSerializer):
    percent_completed = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    saved_amount = serializers.SerializerMethodField()
    trophy_image = serializers.ImageField(read_only=True)
    trophy_type = serializers.CharField(read_only=True)

    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'target_amount', 'target_duration_months',
            'image', 'status', 'created_at', 'achieved_at',
            'saved_amount', 'percent_completed', 'time_remaining',
            'trophy_image', 'trophy_type',
        ]

    def get_percent_completed(self, obj):
        return obj.percent_completed()

    def get_time_remaining(self, obj):
        return obj.time_remaining()

    def get_saved_amount(self, obj):
        return obj.saved_amount()

class GoalSummarySerializer(serializers.Serializer):
    total_saved = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_goals = serializers.IntegerField()
    achieved_goals = serializers.IntegerField()
