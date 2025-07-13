from taskmaster.permissions import IsChildAssignedToChore
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from taskmaster.serializers import RedeemRewardSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from taskmaster.models import Chore
from children.models import Child
from django.db import transaction as db_transaction
from goalgetter.models import Goal
from notifications.models import Notification
from taskmaster.serializers import (
    ChoreReadSerializer,
    ChoreStatusUpdateSerializer,
)
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
        user = self.request.user
        child_id = self.request.query_params.get("childId")

        # Verify logged-in user is the child with this childId
        try:
            child = Child.objects.get(username=user.email)
        except Child.DoesNotExist:
            raise PermissionDenied("You do not have permission to view chores.")

        if not child_id or str(child.id) != child_id:
            raise PermissionDenied("You do not have permission to view this child's chores.")

        queryset = Chore.objects.filter(assigned_to=child)

        status_filter = self.request.query_params.get("status")
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

            # Begin atomic transaction to ensure consistency
            with db_transaction.atomic():
                family_wallet = chore.parent.family_wallet
                child_wallet = chore.assigned_to.wallet
                reward_amount = chore.reward

                if reward_amount > family_wallet.balance:
                    return Response({"detail": "Insufficient funds in family wallet."},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Deduct from family wallet and create transaction
                transaction_obj = family_wallet.create_reward_transaction(
                    child=chore.assigned_to,
                    amount=reward_amount,
                    description=f"Reward for chore '{chore.title}'"
                )

                # Credit child's wallet
                child_wallet.earn(reward_amount)

                # Mark chore as redeemed
                chore.is_redeemed = True
                chore.save()

                # Create notification & realtime notify parent
                Notification.objects.create(
                    parent=chore.parent,
                    type="chore_reward_redeemed",
                    title="Reward Redeemed",
                    message=f"{chore.assigned_to.username} redeemed reward for '{chore.title}'",
                    related_id=chore.id
                )
                notify_parent_realtime(
                    chore.parent,
                    f"{chore.assigned_to.username} redeemed reward for '{chore.title}'",
                    chore.id
                )

                # Check and update child's active goals
                active_goals = Goal.objects.filter(child=chore.assigned_to, status='active')
                for goal in active_goals:
                    goal.check_achievement()

            return Response({
                "detail": "Reward redeemed successfully.",
                "chore": {
                    "title": chore.title,
                    "reward": reward_amount,
                    "is_redeemed": chore.is_redeemed
                },
                "transaction_id": transaction_obj.id,
                "new_child_balance": child_wallet.balance
            }, status=status.HTTP_200_OK)

        except Chore.DoesNotExist:
            return Response({"detail": "Chore not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Server error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
