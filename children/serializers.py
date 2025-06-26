from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Child

User = get_user_model()

class ChildCreateSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    class Meta:
        model = Child
        fields = ('id', 'username', 'name','pin', 'avatar')  
        read_only_fields = ('id',)

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits.")
        if len(value) != 4:
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value

    def validate_username(self, value):
        if Child.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        try:
            pin = validated_data.pop('pin')
            parent = self.context['request'].user  # Get parent from request context
            validated_data['parent'] = parent
            child = Child(**validated_data)
            child.set_pin(pin)
            child.save()
            return child
        except Exception as e:
            raise serializers.ValidationError(f"Server error: {str(e)}")


class ChildUpdateSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=4, required=False)

    class Meta:
        model = Child
        fields = ('username', 'name', 'pin', 'avatar')

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits.")
        if len(value) != 4:
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value

    def validate_username(self, value):
        child_id = self.instance.id if self.instance else None
        if Child.objects.filter(username=value).exclude(id=child_id).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def update(self, instance, validated_data):
        try:
            pin = validated_data.pop('pin', None)
            if pin:
                instance.set_pin(pin)
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Server error: {str(e)}")


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ('id', 'parent', 'username', 'name', 'avatar', 'created_at')
        read_only_fields = ('id', 'created_at')


class ChildLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits.")
        if len(value) != 4:
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value

    def validate(self, data):
        username = data.get('username')
        pin = data.get('pin')
        try:
            child = Child.objects.get(username=username)
        except Child.DoesNotExist:
            raise serializers.ValidationError("Invalid username or PIN.")
        if not child.check_pin(pin):
            raise serializers.ValidationError("Invalid username or PIN.")
        data['child'] = child
        return data
