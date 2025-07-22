from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from django.db import transaction as db_transaction

from .models import Goal, GoalTransaction
from .serializers import GoalSerializer, GoalTransactionSerializer, GoalSummarySerializer
from children.models import Child
from children.authentication import ChildJWTAuthentication  # Import your custom auth


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [ChildJWTAuthentication]

    def get_queryset(self):
        # Only show goals of the authenticated child
        return Goal.objects.filter(child=self.request.child).order_by('-created_at')

    def perform_create(self, serializer):
        # Use authenticated child, ignore client input for child id
        serializer.save(child=self.request.child)

    @action(detail=True, methods=['post'], url_path='contribute')
    def contribute(self, request, pk=None):
        goal = self.get_object()

        if goal.status == 'achieved':
            return Response({"detail": "Goal already achieved."}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get('amount')
        if amount is None:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except Exception:
            return Response({"detail": "Invalid amount provided."}, status=status.HTTP_400_BAD_REQUEST)

        child_wallet = goal.child.wallet
        if amount > child_wallet.balance:
            return Response({"detail": "Insufficient balance in child's wallet."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with db_transaction.atomic():
                # Deduct amount
                child_wallet.balance -= amount
                child_wallet.save()

                serializer = GoalTransactionSerializer(data={'goal': goal.id, 'amount': amount})
                serializer.is_valid(raise_exception=True)
                contribution = serializer.save()

                goal.check_achievement()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"Error processing contribution: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoalSummaryView(APIView):
    serializer_class = GoalSummarySerializer

    permission_classes = [IsAuthenticated]
    authentication_classes = [ChildJWTAuthentication]

    def get(self, request):
        child = request.child
        goals = Goal.objects.filter(child=child)

        total_saved = sum((goal.saved_amount() for goal in goals), Decimal('0.00'))
        active_goals = goals.filter(status='active').count()
        achieved_goals = goals.filter(status='achieved').count()

        data = {
            'total_saved': total_saved,
            'active_goals': active_goals,
            'achieved_goals': achieved_goals,
        }

        serializer = GoalSummarySerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)
