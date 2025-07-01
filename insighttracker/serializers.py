from rest_framework import serializers


class ChoreActivitySerializer(serializers.Serializer):
    chore_title = serializers.CharField()
    reward = serializers.FloatField()
    status = serializers.CharField()  


class ChildChoreActivitySerializer(serializers.Serializer):
    child_name = serializers.CharField()
    activities = ChoreActivitySerializer(many=True)
    total_earned = serializers.FloatField()


class InsightChoreSerializer(serializers.Serializer):
    total_chores_assigned = serializers.IntegerField()
    total_completed_chores = serializers.IntegerField()
    total_pending_chores = serializers.IntegerField()
    child_activities = ChildChoreActivitySerializer(many=True)
