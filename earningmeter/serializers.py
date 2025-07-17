from rest_framework import serializers

class BarChartItemSerializer(serializers.Serializer):
    day = serializers.CharField()
    earned = serializers.DecimalField(max_digits=10, decimal_places=2)
    spent = serializers.DecimalField(max_digits=10, decimal_places=2)

class PieChartSerializer(serializers.Serializer):
    reward_saved = serializers.DecimalField(max_digits=10, decimal_places=2)
    reward_spent = serializers.DecimalField(max_digits=10, decimal_places=2)

class ActivityItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    activity = serializers.CharField()
    amount = serializers.CharField()
    status = serializers.CharField()
    date = serializers.CharField()

class SummarySerializer(serializers.Serializer):
    bar_chart = BarChartItemSerializer(many=True)
    pie_chart = PieChartSerializer()
    recent_activities = ActivityItemSerializer(many=True)


class EarningTotalsSerializer(serializers.Serializer):
    total_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_saved = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
