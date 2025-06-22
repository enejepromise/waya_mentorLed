from rest_framework import serializers
from .models import Task
from django.utils import timezone

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    assignedTo = serializers.UUIDField(write_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'reward',
            'due_date',
            'assignedTo',
            'status',
            'created_at',
            'completed_at',
        )
        read_only_fields = ('id', 'status', 'created_at', 'completed_at')

    def validate(self, attrs):
        request = self.context.get('request')
        parent = request.user

        assigned_to_id = attrs.pop('assignedTo')
        from children.models import Child  

        try:
            assigned_to = Child.objects.get(id=assigned_to_id)
        except Child.DoesNotExist:
            raise serializers.ValidationError("Assigned child not found.")

        if assigned_to.parent != parent:
            raise serializers.ValidationError("You cannot assign a task to a child that is not yours.")

        attrs['assigned_to'] = assigned_to
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
