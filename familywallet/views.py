from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from .serializers import MakePaymentSerializer, WalletPinSerializer
from rest_framework import generics
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import timedelta
from decimal import Decimal

from .models import FamilyWallet, ChildWallet, Transaction, Allowance
from .serializers import (
    FamilyWalletSerializer,
    ChildWalletSerializer,
    TransactionSerializer,
    DashboardStatsSerializer,
    AddFundsSerializer,
    CompleteTransactionSerializer,
    AllowanceSerializer
)
from children.models import Child


class IsParentPermission(permissions.BasePermission):
    """Allow access only to authenticated parents."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == request.user.ROLE_PARENT


class FamilyWalletViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyWalletSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        return FamilyWallet.objects.filter(parent=self.request.user)

    def get_object(self):
        return self.request.user.family_wallet

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        try:
            family_wallet = request.user.family_wallet
            children_wallets = ChildWallet.objects.for_parent(request.user)

            stats = {
                'family_wallet_balance': family_wallet.balance,
                'total_rewards_sent': family_wallet.get_total_rewards_sent(),
                'total_rewards_pending': family_wallet.get_total_rewards_pending(),
                'children_count': children_wallets.count(),
                'total_children_balance': (
                    children_wallets.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
                )
            }
            serializer = DashboardStatsSerializer(stats)
            return Response(serializer.data)

        except FamilyWallet.DoesNotExist:
            return Response({'error': 'Family wallet not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def add_funds(self, request):
        serializer = AddFundsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                family_wallet = request.user.family_wallet
                transaction_obj = family_wallet.add_funds(
                    amount=serializer.validated_data['amount'],
                    description=serializer.validated_data['description'],
                    created_by=request.user
                )
                return Response({
                    'message': 'Funds added successfully',
                    'new_balance': family_wallet.balance,
                    'transaction_id': transaction_obj.id
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def earnings_chart_data(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        transactions = Transaction.objects.filter(
            family_wallet__parent=request.user,
            transaction_type=Transaction.TYPE_REWARD,
            status=Transaction.STATUS_COMPLETED,
            created_at__gte=start_date
        ).select_related('child')

        chart_data = {}
        for tx in transactions:
            date_key = tx.created_at.date().isoformat()
            name = tx.child.name if tx.child else 'Unknown'
            chart_data.setdefault(date_key, {})
            chart_data[date_key].setdefault(name, Decimal('0.00'))
            chart_data[date_key][name] += tx.amount

        return Response(chart_data)

    @action(detail=False, methods=['get'])
    def savings_breakdown(self, request):
        children_wallets = ChildWallet.objects.for_parent(request.user)
        breakdown_data = [
            {
                'child_name': wallet.child.username,
                'reward_saved': wallet.balance,
                'reward_spent': wallet.total_spent,
                'total_earned': wallet.total_earned,
                'savings_rate': wallet.savings_rate
            }
            for wallet in children_wallets
        ]
        return Response(breakdown_data)

    @action(detail=False, methods=['post'], url_path='transfer')
    def transfer(self, request):
        child_id = request.data.get('child_id')
        amount = request.data.get('amount')

        if not child_id or not amount:
            return Response({'error': 'child_id and amount are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except Exception:
            return Response({'error': 'Invalid amount provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            child = Child.objects.get(id=child_id, parent=request.user)
        except Child.DoesNotExist:
            return Response({'error': 'Child not found or does not belong to you.'}, status=status.HTTP_404_NOT_FOUND)

        family_wallet = request.user.family_wallet
        if amount > family_wallet.balance:
            return Response({'error': 'Insufficient wallet balance.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction = family_wallet.create_reward_transaction(
            child=child,
            amount=amount,
            description='Manual fund transfer'
        )

        return Response({
            'message': 'Transfer successful.',
            'transaction_id': transaction.id,
            'new_balance': str(family_wallet.balance)
        }, status=status.HTTP_200_OK)


class ChildWalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChildWalletSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        return ChildWallet.objects.for_parent(self.request.user)

    @action(detail=False, methods=['get'])
    def analysis(self, request):
        user = request.user
        wallet = user.family_wallet

        transactions = Transaction.objects.filter(family_wallet=wallet).select_related('child')
        activities = [
            {
                'name': tx.child.name if tx.child else 'N/A',
                'activity': tx.description,
                'amount': tx.amount,
                'status': tx.status,
                'date': tx.created_at.date()
            }
            for tx in transactions
        ]

        savings_breakdown = []
        for wallet in ChildWallet.objects.for_parent(user):
            savings_breakdown.append({
                'child_name': wallet.child.username,
                'reward_saved': wallet.balance,
                'reward_spent': wallet.total_spent,
                'total_earned': wallet.total_earned,
                'savings_rate': wallet.savings_rate
            })

        return Response({
            'family_wallet_balance': wallet.balance,
            'total_rewards_sent': wallet.get_total_rewards_sent(),
            'total_rewards_pending': wallet.get_total_rewards_pending(),
            'activities': activities,
            'savings_breakdown': savings_breakdown
        })


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            family_wallet__parent=self.request.user
        ).select_related('child', 'created_by')

        status_filter = self.request.query_params.get('status')
        type_filter = self.request.query_params.get('type')
        child_id = self.request.query_params.get('child_id')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if type_filter:
            queryset = queryset.filter(transaction_type=type_filter)
        if child_id:
            queryset = queryset.filter(child_id=child_id)

        return queryset

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        transaction_obj = self.get_object()
        try:
            with db_transaction.atomic():
                transaction_obj.complete_transaction()

            serializer = self.get_serializer(transaction_obj)
            return Response({
                'message': 'Transaction completed successfully',
                'transaction': serializer.data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        transaction_obj = self.get_object()
        try:
            transaction_obj.cancel_transaction()
            serializer = self.get_serializer(transaction_obj)
            return Response({
                'message': 'Transaction cancelled successfully',
                'transaction': serializer.data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def complete_multiple(self, request):
        serializer = CompleteTransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction_ids = serializer.validated_data['transaction_ids']
            try:
                with db_transaction.atomic():
                    transactions = Transaction.objects.filter(
                        id__in=transaction_ids,
                        family_wallet__parent=request.user,
                        status=Transaction.STATUS_PENDING
                    )

                    completed_count = 0
                    for tx in transactions:
                        tx.complete_transaction()
                        completed_count += 1

                return Response({
                    'message': f'{completed_count} transactions completed successfully',
                    'completed_count': completed_count
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        limit = int(request.query_params.get('limit', 10))
        transactions = self.get_queryset()[:limit]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class AllowanceViewSet(viewsets.ModelViewSet):
    serializer_class = AllowanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        parent = self.request.user
        queryset = Allowance.objects.filter(parent=parent)

        child_id = self.request.query_params.get('child_id')
        status = self.request.query_params.get('status')

        if child_id:
            queryset = queryset.filter(child__id=child_id)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)

# Set/Update wallet PIN
@action(detail=False, methods=['post'], url_path='set-pin')
def set_wallet_pin(self, request):
    serializer = WalletPinSerializer(data=request.data)
    if serializer.is_valid():
        wallet = request.user.family_wallet
        pin = serializer.validated_data['pin']
        wallet.pin = make_password(pin)
        wallet.save()
        return Response({'message': 'PIN set successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Make payment to child for chore (with PIN)
@action(detail=False, methods=['post'], url_path='make-payment')
def make_payment(self, request):
    serializer = MakePaymentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        txn = serializer.save()
        return Response({
            'message': 'Payment successful',
            'transaction_id': txn.id,
            'amount': txn.amount
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
