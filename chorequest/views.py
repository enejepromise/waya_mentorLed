from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from taskmaster.models import Chore
from .serializers import (
    ChoreQuestSerializer,
    CompleteChoreSerializer,
    RedeemRewardSerializer
)
from .permissions import IsChild
from django.utils import timezone
from notifications.utils import send_notification, notify_parent_realtime


class ChoreQuestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for the child dashboard to list, complete, and redeem chores.
    Authenticated via ChildAuthentication.
    """
    serializer_class = ChoreQuestSerializer
    permission_classes = [IsChild]

    def get_queryset(self):
        # Use request.child set by ChildAuthentication
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

            # Notify parent in real-time
            parent_user = request.user  # request.user is the parent, per ChildAuthentication
            notify_parent_realtime(parent_user, f"{request.child.name} completed the chore '{chore.title}'", chore_id=chore.id)

            return Response({'message': 'Chore marked as completed. Parent has been notified.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='redeem')
    def redeem_reward(self, request):
        serializer = RedeemRewardSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            chore = serializer.validated_data['chore']

            if chore.assigned_to != request.child:
                return Response({'error': 'You can only redeem your own chores.'}, status=status.HTTP_403_FORBIDDEN)

            if chore.status != 'approved':
                return Response({'error': 'Chore reward is not yet approved by your parent.'}, status=status.HTTP_400_BAD_REQUEST)

            # update chore status
            chore.status = 'rewarded'
            chore.save()

            # reward added to child wallet
            wallet = chore.assigned_to.wallet
            wallet.earn(chore.reward)

            # Notify child
            send_notification(request.child.user, f"Reward for completing the chore '{chore.title}' has been added to your wallet!")

            return Response({
                'message': f"Reward of ₦{chore.reward} added to your wallet!",
                'new_balance': wallet.balance
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
