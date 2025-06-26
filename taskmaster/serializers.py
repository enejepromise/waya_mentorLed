from rest_framework import serializers
from .models import Task
from django.utils import timezone
from children.models import Child



class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.UUIDField(write_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'parent_id'
            'title',
            'description',
            'reward',
            'due_date',
            'assigned_to',
            'status',
            'created_at',
            'completed_at',
        )
        read_only_fields = ('id', 'status', 'created_at', 'completed_at')

    def validate(self, attrs):
        request = self.context.get('request')
        parent = request.user

        assigned_to_id = attrs.pop('assigned_to')

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
    assignedTo = serializers.UUIDField(source='assigned_to.id')
    parentId = serializers.UUIDField(source='parent.id')
    amount = serializers.DecimalField(source='reward', max_digits=10, decimal_places=2)
    createdAt = serializers.DateTimeField(source='created_at')
    completedAt = serializers.DateTimeField(source='completed_at')
    category = serializers.CharField(required=False)  # Optional, for chores endpoint

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'assignedTo',
            'status',
            'amount',
            'createdAt',
            'completedAt',
            'parentId',
            'category',
        )

