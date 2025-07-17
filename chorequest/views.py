from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from taskmaster.models import Chore
from .serializers import (
    ChoreQuestSerializer,
    CompleteChoreSerializer,
    RedeemRewardSerializer
)
from children.authentication import ChildJWTAuthentication
from .permissions import IsChild
from notifications.utils import send_notification, notify_parent_realtime


class ChoreQuestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for children to list, complete, and redeem their chores.
    Authenticated via ChildJWTAuthentication.
    """
    serializer_class = ChoreQuestSerializer
    permission_classes = [IsChild]
    authentication_classes = [ChildJWTAuthentication]

    def get_queryset(self):
        return Chore.objects.filter(assigned_to=self.request.child)

    @action(detail=False, methods=['post'], url_path='complete')
    def mark_complete(self, request):
        serializer = CompleteChoreSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            chore = serializer.validated_data['chore']
            if chore.assigned_to != request.child:
                return Response({'error': 'You can only complete your own chores.'}, status=status.HTTP_403_FORBIDDEN)

            chore.status = 'completed'
            chore.completed_at = timezone.now()
            chore.save()

            notify_parent_realtime(
                user=chore.parent,
                message=f"{request.child.name} completed the chore '{chore.title}'",
                chore_id=chore.id
            )

            return Response({'message': 'Chore marked as completed.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='redeem')
    def redeem_reward(self, request):
        serializer = RedeemRewardSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            chore = serializer.validated_data['chore']

            if chore.assigned_to != request.child:
                return Response({'error': 'You can only redeem your own chores.'}, status=status.HTTP_403_FORBIDDEN)

            if chore.status != 'approved':
                return Response({'error': 'Chore must be approved before redeeming.'}, status=status.HTTP_400_BAD_REQUEST)

            chore.is_redeemed = True
            chore.save()

            wallet = chore.assigned_to.wallet
            wallet.earn(chore.reward)

            send_notification(
                request.child.user,
                f"Reward for completing the chore '{chore.title}' has been added to your wallet!"
            )

            return Response({
                'message': f"Reward of ₦{chore.reward} added to your wallet.",
                'new_balance': wallet.balance
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
