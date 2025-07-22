from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from collections import defaultdict
import uuid
from .serializers import PaystackPaymentInitSerializer, PaystackPaymentVerifySerializer
from rest_framework.decorators import action
from django.db.models import Sum
from utils.paystack import initialize_payment, verify_payment


from django.contrib.auth.hashers import make_password
from .serializers import (
    MakePaymentSerializer, WalletPinSerializer,
    FamilyWalletSerializer, ChildWalletSerializer,
    TransactionSerializer, DashboardStatsSerializer,
    AddFundsSerializer, CompleteTransactionSerializer,
    AllowanceSerializer
)
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import timedelta
from decimal import Decimal
from .models import FamilyWallet, ChildWallet, Transaction, Allowance
from children.models import Child

class IsParentPermission(permissions.BasePermission):
    """Allow access only to authenticated parents."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == request.user.ROLE_PARENT

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

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
            children_wallets = ChildWallet.objects.filter(child__parent=request.user)

            stats = {
                'family_wallet_balance': family_wallet.balance,
                'total_rewards_sent': family_wallet.get_total_sent(),
                'total_rewards_pending': family_wallet.get_total_pending(),
                'children_count': children_wallets.count(),
                'total_children_balance': children_wallets.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
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
            parent=request.user,
            type='chore_reward',
            status='paid',
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
        children_wallets = ChildWallet.objects.filter(child__parent=request.user)
        breakdown_data = [
            {
                'child_name': wallet.child.name,
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

        try:
            transaction = family_wallet.create_reward_transaction(
                child=child,
                amount=amount,
                description='Manual fund transfer'
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Transfer successful.',
            'transaction_id': transaction.id,
            'new_balance': str(family_wallet.balance)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='reward_bar_chart')
    def reward_bar_chart(self, request):
        """
        Returns bar chart data: earnings per child per day, plus highest & lowest earner.
        """
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        transactions = Transaction.objects.filter(
            parent=request.user,
            type='chore_reward',
            status='paid',
            created_at__gte=start_date
        ).select_related('child')

        chart_data = defaultdict(lambda: defaultdict(Decimal))
        total_by_child = defaultdict(Decimal)

        for tx in transactions:
            date_key = tx.created_at.strftime('%B %d, %Y')  # e.g., "April 22, 2025"
            child_name = tx.child.name if tx.child else "Unknown"
            chart_data[date_key][child_name] += tx.amount
            total_by_child[child_name] += tx.amount

        if total_by_child:
            highest_earner = max(total_by_child.items(), key=lambda x: x[1])
            lowest_earner = min(total_by_child.items(), key=lambda x: x[1])
        else:
            highest_earner = lowest_earner = ("None", Decimal("0.00"))

        return Response({
            "chart_data": chart_data,
            "highest_earner": {
                "name": highest_earner[0],
                "amount": highest_earner[1]
            },
            "lowest_earner": {
                "name": lowest_earner[0],
                "amount": lowest_earner[1]
            }
        })

    @action(detail=False, methods=['get'], url_path='reward_pie_chart')
    def reward_pie_chart(self, request):
        """
        Returns pie chart data: reward spent vs reward saved per child.
        """
        children_wallets = ChildWallet.objects.filter(child__parent=request.user)

        pie_data = []
        for wallet in children_wallets:
            child_name = wallet.child.name
            saved = wallet.balance
            spent = wallet.total_spent

            pie_data.append({
                "child_name": child_name,
                "reward_saved": saved,
                "reward_spent": spent,
                "total": saved + spent
            })

        return Response(pie_data)

    @action(detail=False, methods=['get'], url_path='wallet-summary')
    def wallet_summary(self, request):
        """
        Return a summary breakdown of the family wallet:
        - Total balance
        - Total reward sent (paid chore rewards)
        - Total reward pending (pending chore rewards)
        """
        try:
            family_wallet = request.user.family_wallet

            total_reward_sent = Transaction.objects.filter(
                parent=request.user,
                type='chore_reward',
                status='paid'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            total_reward_pending = Transaction.objects.filter(
                parent=request.user,
                type='chore_reward',
                status='pending'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            return Response({
                'wallet_balance': family_wallet.balance,
                'total_reward_sent': total_reward_sent,
                'total_reward_pending': total_reward_pending
            })
        except FamilyWallet.DoesNotExist:
            return Response({'error': 'Family wallet not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='paystack/initiate')
    def initiate_paystack_payment(self, request):
        serializer = PaystackPaymentInitSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            reference = str(uuid.uuid4())

            response = initialize_payment(request.user.email, amount, reference)

            if response.get("status"):
                Transaction.objects.create(
                    parent=request.user,
                    type="wallet_funding",
                    amount=amount,
                    description="Funding wallet via Paystack",
                    status="pending",
                    reference=reference
                )
                return Response({
                    "authorization_url": response["data"]["authorization_url"],
                    "reference": reference
                }, status=200)
            return Response({"error": "Payment initialization failed."}, status=400)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='paystack/verify')
    def verify_paystack_payment(self, request):
        serializer = PaystackPaymentVerifySerializer(data=request.data)
        if serializer.is_valid():
            reference = serializer.validated_data['reference']

            tx = Transaction.objects.filter(
                parent=request.user,
                reference=reference,
                type="wallet_funding",
                status="pending"
            ).first()

            if not tx:
                return Response({"error": "Transaction not found or already processed."}, status=400)

            response = verify_payment(reference)

            if response.get("data", {}).get("status") == "success":
                wallet = request.user.family_wallet
                wallet.add_funds(tx.amount, "Paystack Wallet Funding", request.user)
                tx.complete_transaction()
                return Response({"message": "Wallet funded successfully!"}, status=200)

            return Response({"error": "Verification failed."}, status=400)
        return Response(serializer.errors, status=400)

class ChildWalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChildWalletSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        return ChildWallet.objects.filter(child__parent=self.request.user)

    @action(detail=False, methods=['get'])
    def analysis(self, request):
        user = request.user
        wallet = user.family_wallet

        transactions = Transaction.objects.filter(parent=user).select_related('child')
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

        savings_breakdown = [
            {
                'child_name': wallet.child.name,
                'reward_saved': wallet.balance,
                'reward_spent': wallet.total_spent,
                'total_earned': wallet.total_earned,
                'savings_rate': wallet.savings_rate
            }
            for wallet in ChildWallet.objects.filter(child__parent=user)
        ]

        return Response({
            'family_wallet_balance': wallet.balance,
            'total_rewards_sent': wallet.get_total_sent(),
            'total_rewards_pending': wallet.get_total_pending(),
            'activities': activities,
            'savings_breakdown': savings_breakdown
        })


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        queryset = Transaction.objects.filter(parent=self.request.user).select_related('child')

        status_filter = self.request.query_params.get('status')
        type_filter = self.request.query_params.get('type')
        child_id = self.request.query_params.get('child_id')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if type_filter:
            queryset = queryset.filter(type=type_filter)
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
                        parent=request.user,
                        status='pending'
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
        transactions = self.get_queryset().order_by('-created_at')[:limit]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

class AllowanceViewSet(viewsets.ModelViewSet):
    serializer_class = AllowanceSerializer
    permission_classes = [IsParentPermission]

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

class WalletViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = WalletPinSerializer
    permission_classes = [IsParentPermission]

    @action(detail=False, methods=['post'])
    def set_pin(self, request):
        serializer = WalletPinSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically create the family wallet if it doesn't exist
            wallet, created = FamilyWallet.objects.get_or_create(parent=request.user)

            # Automatically create child wallets for each child
            children = Child.objects.filter(parent=request.user)
            child_wallets_created = 0
            for child in children:
                _, cw_created = ChildWallet.objects.get_or_create(child=child)
                if cw_created:
                    child_wallets_created += 1

            # Set PIN
            pin = serializer.validated_data['pin']
            wallet.pin = make_password(pin)
            wallet.save()

            return Response({
                'message': 'PIN set successfully',
                'wallet_created': created,
                'child_wallets_created': child_wallets_created
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
    
    @action(detail=False, methods=['post'])
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
    @action(detail=False, methods=['get'])
    def pin_status(self, request):
        try:
            wallet = FamilyWallet.objects.get(parent=request.user)
            pin_is_set = wallet.pin is not None and wallet.pin != ''
        except FamilyWallet.DoesNotExist:
            pin_is_set = False

        return Response({'pin_set': pin_is_set})