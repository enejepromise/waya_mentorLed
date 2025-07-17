# chorequest/serializers.py

from rest_framework import serializers


class BarChartItemSerializer(serializers.Serializer):
    day = serializers.CharField()
    earned = serializers.DecimalField(max_digits=10, decimal_places=2)
    spent = serializers.DecimalField(max_digits=10, decimal_places=2)


class PieChartSerializer(serializers.Serializer):
    reward_saved = serializers.DecimalField(max_digits=10, decimal_places=2)
    reward_spent = serializers.DecimalField(max_digits=10, decimal_places=2)


class SummarySerializer(serializers.Serializer):
    bar_chart = BarChartItemSerializer(many=True)
    pie_chart = PieChartSerializer()
