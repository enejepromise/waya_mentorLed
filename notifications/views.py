from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from children.models import Child
from children.serializers import ChildSerializer
from .models import Notification, Reward
from .serializers import (
    UserProfileSerializer,
    NotificationRewardSerializer,  # Use the renamed serializer here
    PasswordResetSerializer,
    NotificationSerializer,
    EmptySerializer
)

User = get_user_model()

# ---- User Profile View ----
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---- Child Profile View ----
class ChildView(generics.RetrieveUpdateAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def get_object(self):
        child_id = self.kwargs.get("child_id")
        return self.get_queryset().get(id=child_id)


# ---- Password Reset View ----
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


# ---- Reward Settings View ----
class RewardView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationRewardSerializer  # Use NotificationRewardSerializer here
    permission_classes = [IsAuthenticated]

    def get_object(self):
        setting, _ = Reward.objects.get_or_create(user=self.request.user)
        return setting


# ---- Notification List View ----
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        unread = self.request.query_params.get("unread")
        qs = Notification.objects.filter(parent=user).order_by("-created_at")
        if unread and unread.lower() == "true":
            qs = qs.filter(is_read=False)
        return qs


# ---- Mark Notification as Read View ----
class MarkNotificationReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer  # Required by DRF even if not used
    queryset = Notification.objects.all()
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.parent != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        notification.is_read = True
        notification.save()
        return Response({"success": True})
