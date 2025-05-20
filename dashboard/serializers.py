# dashboard/serializers.py
from rest_framework import serializers
from .models import Child

class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'username', 'avatar', 'created_at']


class ChildCreateSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True)

    class Meta:
        model = Child
        fields = ['username', 'avatar', 'pin']

    def validate_pin(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value

    def create(self, validated_data):
        raw_pin = validated_data.pop('pin')
        child = Child(**validated_data)
        child.set_pin(raw_pin)
        child.parent = self.context['request'].user
        child.save()
        return child
