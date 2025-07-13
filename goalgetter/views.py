from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from decimal import Decimal
from django.db import transaction as db_transaction

from .models import Goal, GoalTransaction
from .serializers import GoalSerializer, GoalTransactionSerializer, GoalSummarySerializer
from children.models import Child

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(child__parent=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        child_id = self.request.data.get('child')
        try:
            child = Child.objects.get(id=child_id, parent=self.request.user)
        except Child.DoesNotExist:
            raise ValidationError("Child not found or does not belong to you.")
        serializer.save(child=child)

    @action(detail=True, methods=['post'], url_path='contribute')
    def contribute(self, request, pk=None):
        """
        Endpoint to contribute an amount toward a goal.
        """
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

        # Check if child's wallet has sufficient balance
        child_wallet = goal.child.wallet
        if amount > child_wallet.balance:
            return Response({"detail": "Insufficient balance in child's wallet."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with db_transaction.atomic():
                # Deduct from child's wallet
                child_wallet.balance -= amount
                child_wallet.save()

                # Use serializer to validate and create GoalTransaction
                serializer = GoalTransactionSerializer(data={'goal': goal.id, 'amount': amount})
                serializer.is_valid(raise_exception=True)
                contribution = serializer.save()

                # Check if goal is achieved after contribution
                goal.check_achievement()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": f"Error processing contribution: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoalSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        goals = Goal.objects.filter(child__parent=user)

        # Use Decimal for accuracy
        total_saved = sum((goal.saved_amount() for goal in goals), Decimal('0.00'))
        active_goals = goals.filter(status='active').count()
        achieved_goals = goals.filter(status='achieved').count()

        data = {
            'total_saved': total_saved,
            'active_goals': active_goals,
            'achieved_goals': achieved_goals,
        }

        serializer = GoalSummarySerializer(data=data)
        serializer.is_valid(raise_exception=True)  # Validate data before returning

        return Response(serializer.data)
