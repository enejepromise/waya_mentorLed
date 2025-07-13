from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from children.models import Child
from .models import NotificationSettings, RewardSettings
from .serializers import (
    UserProfileSerializer,
    ChildSerializer,
    PasswordResetSerializer,
    NotificationSettingSerializer,
    RewardSettingSerializer
)

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChildView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def get_object(self):
        child_id = self.kwargs.get("child_id")
        return self.get_queryset().get(id=child_id)

class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['current_password']):
            return Response({"detail": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Auto-create if not exists
        setting, _ = NotificationSettings.objects.get_or_create(user=self.request.user)
        return setting


class RewardSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = RewardSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        setting, _ = RewardSettings.objects.get_or_create(user=self.request.user)
        return setting
    
class ChildListCreateView(generics.ListCreateAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)
