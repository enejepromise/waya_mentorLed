from rest_framework import serializers
from .models import Chore
from children.models import Child

class ChoreCreateUpdateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.UUIDField(write_only=True)

    class Meta:
        model = Chore
        fields = (
            'id',
            'title',
            'description',
            'reward',
            'due_date',
            'assigned_to',
            'status',
            'created_at',
            'completed_at',
            'category',
            'is_redeemed',
        )
        read_only_fields = ('id', 'status', 'created_at', 'completed_at')

    def validate(self, attrs):
        request = self.context.get('request')
        parent = request.user

        assigned_to_id = attrs.get('assigned_to')
        if not assigned_to_id:
            raise serializers.ValidationError({"assigned_to": "This field is required."})

        try:
            assigned_to = Child.objects.get(id=assigned_to_id)
        except Child.DoesNotExist:
            raise serializers.ValidationError({"assigned_to": "Assigned child not found."})

        if assigned_to.parent != parent:
            raise serializers.ValidationError("You cannot assign a chore to a child that is not yours.")

        attrs['assigned_to'] = assigned_to
        return attrs

    def create(self, validated_data):
        validated_data['parent'] = self.context['request'].user
        return super().create(validated_data)


class ChoreStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Chore.STATUS_CHOICES)

    class Meta:
        model = Chore
        fields = ('status',)

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()
        return instance


class ChoreReadSerializer(serializers.ModelSerializer):
    assignedTo = serializers.UUIDField(source='assigned_to.id')
    # Remove or fix assignedToName depending on your Child model
    # assignedToName = serializers.CharField(source='assigned_to.name', default='') # Uncomment if Child has .name
    assignedToUsername = serializers.CharField(source='assigned_to.username')
    parentId = serializers.UUIDField(source='parent.id')
    amount = serializers.DecimalField(source='reward', max_digits=10, decimal_places=2)
    createdAt = serializers.DateTimeField(source='created_at')
    completedAt = serializers.DateTimeField(source='completed_at', allow_null=True)  # may be null
    category = serializers.CharField(required=False, allow_blank=True)
    isRedeemed = serializers.BooleanField(source='is_redeemed')

    class Meta:
        model = Chore
        fields = (
            'id',
            'title',
            'description',
            'assignedTo',
            # 'assignedToName',  # Remove if no `name` field on Child model
            'assignedToUsername',
            'status',
            'amount',
            'createdAt',
            'completedAt',
            'parentId',
            'category',
            'isRedeemed',   # Must match serializer field name exactly (capital R)
        )

class RedeemRewardSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(source='reward', max_digits=10, decimal_places=2)
    isRedeemed = serializers.BooleanField(source='is_redeemed')

    class Meta:
        model = Chore
        fields = ['title', 'amount', 'isRedeemed']


class ChoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chore
        fields = "__all__"


class EmptySerializer(serializers.Serializer):
    pass
