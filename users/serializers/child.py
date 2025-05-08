# serializers/child.py
from rest_framework import serializers
from users.models import Child

class ChildRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new child user.
    Only accessible by a parent user.
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Child
        fields = ['username', 'fullname', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        parent = self.context['request'].user
        child = Child.objects.create(parent=parent, **validated_data)
        child.set_password(password)
        child.save()
        return child


class ChildLoginSerializer(serializers.Serializer):
    """
    Serializer for child login using username and password.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            child = Child.objects.get(username=data['username'])
        except Child.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password.")

        if not child.check_password(data['password']):
            raise serializers.ValidationError("Invalid username or password.")

        data['child'] = child
        return data


class ChildProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing child details.
    """
    class Meta:
        model = Child
        fields = ['id', 'username', 'fullname', 'created_at']
