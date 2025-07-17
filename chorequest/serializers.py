from rest_framework import serializers
from taskmaster.models import Chore

class ChoreQuestSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='assigned_to.name', read_only=True)

    class Meta:
        model = Chore
        fields = ['id', 'title', 'description', 'status', 'reward', 'child_name', 'completed_at']
        read_only_fields = ['id', 'child_name', 'reward', 'completed_at', 'status']


class CompleteChoreSerializer(serializers.Serializer):
    chore_id = serializers.UUIDField()

    def validate_chore_id(self, value):
        child = self.context['request'].child  # from ChildAuthentication

        try:
            chore = Chore.objects.get(id=value, assigned_to=child)
        except Chore.DoesNotExist:
            raise serializers.ValidationError("Chore not found or not assigned to you.")

        if chore.status != 'pending':
            raise serializers.ValidationError("Only pending chores can be completed.")

        # Attach chore to validated_data so we don't fetch again in view
        self.context['chore'] = chore
        return value

    def validate(self, data):
        data['chore'] = self.context['chore']
        return data


class RedeemRewardSerializer(serializers.Serializer):
    chore_id = serializers.UUIDField()

    def validate_chore_id(self, value):
        child = self.context['request'].child  # from ChildAuthentication

        try:
            chore = Chore.objects.get(id=value, assigned_to=child)
        except Chore.DoesNotExist:
            raise serializers.ValidationError("Chore not found or not assigned to you.")

        if chore.status != 'approved':
            raise serializers.ValidationError("Chore must be approved before redeeming.")

        self.context['chore'] = chore
        return value

    def validate(self, data):
        data['chore'] = self.context['chore']
        return data
