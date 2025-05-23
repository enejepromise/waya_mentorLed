from rest_framework import serializers
from .models import Child
from .utils import make_pin  # Make sure you have this utility function defined


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'username', 'avatar', 'created_at']
        extra_kwargs = {'pin': {'write_only': True}}


class ChildCreateSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True)

    class Meta:
        model = Child
        fields = ['username', 'avatar', 'pin']
    
    def validate_username(self, value):
        if Child.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_pin(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value

    def create(self, validated_data):
        validated_data['pin'] = make_pin(validated_data['pin'])  # 🔐 Replace plain pin with hashed one
        validated_data['parent'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'pin' in validated_data:
            validated_data['pin'] = make_pin(validated_data['pin'])  # 🔐 Use make_pin on update too
        return super().update(instance, validated_data)
