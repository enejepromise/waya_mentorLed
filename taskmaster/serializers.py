from rest_framework import serializers
from .models import Task

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    assignedTo = serializers.UUIDField(source='assigned_to.id')
    parentId = serializers.UUIDField(source='parent.id')

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'reward',
            'due_date',
            'assignedTo',
            'parentId',
            'status',
            'created_at',
            'completed_at',
        )
        read_only_fields = ('id', 'status', 'created_at', 'completed_at')

    def validate(self, attrs):
        assigned_to = attrs.get('assigned_to')
        parent = attrs.get('parent')

        if assigned_to.parent != parent:
            raise serializers.ValidationError("Child does not belong to the specified parent.")

        if attrs.get('due_date') and attrs['due_date'] < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")

        return attrs


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)

    class Meta:
        model = Task
        fields = ('status',)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()
        return instance


class TaskReadSerializer(serializers.ModelSerializer):
    assignedTo = serializers.CharField(source='assigned_to.username')
    parentId = serializers.CharField(source='parent.id')

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'reward',
            'due_date',
            'assignedTo',
            'parentId',
            'status',
            'created_at',
            'completed_at',
        )
