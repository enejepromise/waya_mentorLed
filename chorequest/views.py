from django.shortcuts import render
from taskmaster.permissions import IsChildAssignedToChore
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from taskmaster.serializers import RedeemRewardSerializer
# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from taskmaster.models import Chore
from notifications.models import Notification
from taskmaster.serializers import (
    ChoreReadSerializer,
    ChoreStatusUpdateSerializer,
)
from taskmaster.permissions import IsChildAssignedToChore
from taskmaster.models import notify_parent_realtime


class ChildChoreListView(generics.ListAPIView):
    """
    GET /api/chorequest/chores/?childId=<uuid>&status=pending|completed

    Returns list of chores assigned to a specific child.
    Children can see both pending and completed chores, including their rewards.
    """
    serializer_class = ChoreReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        child_id = self.request.query_params.get("childId")
        status_filter = self.request.query_params.get("status")

        queryset = Chore.objects.filter(assigned_to__id=child_id)

        if status_filter in [Chore.STATUS_PENDING, Chore.STATUS_COMPLETED, Chore.STATUS_MISSED]:
            queryset = queryset.filter(status=status_filter)

        return queryset

class ChildChoreStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/chorequest/chores/<chore_id>/status/

    Allows a child to mark their chore as completed.
    Sends notification to the parent when completed.
    """
    serializer_class = ChoreStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsChildAssignedToChore]
    queryset = Chore.objects.all()

    def get_object(self):
        chore = super().get_object()
        self.check_object_permissions(self.request, chore)
        return chore

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        previous_status = instance.status
        response = super().patch(request, *args, **kwargs)

        if instance.status == Chore.STATUS_COMPLETED and previous_status != Chore.STATUS_COMPLETED:
            Notification.objects.create(
                parent=instance.parent,
                type="chore_completed",
                title="Chore Completed",
                message=f"{instance.assigned_to.username} completed '{instance.title}'",
                related_id=instance.id
            )
            notify_parent_realtime(
                instance.parent,
                f"{instance.assigned_to.username} completed '{instance.title}'",
                instance.id
            )

        return response

class RedeemRewardView(APIView):
    serializer_class = RedeemRewardSerializer  
    """
    PATCH /api/chorequest/chores/<chore_id>/redeem/

    Lets a child redeem a reward after completing a chore.
    """
    permission_classes = [IsAuthenticated, IsChildAssignedToChore]

    def patch(self, request, chore_id):
        try:
            chore = Chore.objects.get(id=chore_id)
            self.check_object_permissions(request, chore)

            if chore.status != Chore.STATUS_COMPLETED:
                return Response({"detail": "Chore must be completed before redeeming."},
                                status=status.HTTP_400_BAD_REQUEST)

            if chore.is_redeemed:
                return Response({"detail": "Reward already redeemed."},
                                status=status.HTTP_400_BAD_REQUEST)

            chore.is_redeemed = True
            chore.save()

            return Response({
                "detail": "Reward redeemed successfully.",
                "chore": {
                    "title": chore.title,
                    "reward": chore.reward,
                    "is_redeemed": chore.is_redeemed
                }
            }, status=status.HTTP_200_OK)

        except Chore.DoesNotExist:
            return Response({"detail": "Chore not found."},
                            status=status.HTTP_404_NOT_FOUND)

