from rest_framework import serializers
from decimal import Decimal
from .models import FamilyWallet, ChildWallet, Transaction, Allowance
from children.models import Child

# Wallet Serializer
class FamilyWalletSerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(source='parent.id', read_only=True)

    class Meta:
        model = FamilyWallet
        fields = ['id', 'parent_id', 'balance', 'currency', 'last_updated']
        read_only_fields = fields


# Add Funds
class AddFundsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(max_length=255)

    def validate_amount(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Amount must be positive.")
        return value


# Set or Update Wallet PIN
class WalletPinSerializer(serializers.Serializer):
    pin = serializers.CharField(min_length=4, max_length=4)

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value


# Child Wallet Info
class ChildWalletSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.name', read_only=True)

    class Meta:
        model = ChildWallet
        fields = ['id', 'child_name', 'balance', 'total_earned', 'total_spent', 'savings_rate']
        read_only_fields = fields


# Single Transaction
class TransactionSerializer(serializers.ModelSerializer):
    family_wallet_id = serializers.UUIDField(source='family_wallet.id', read_only=True)
    child_id = serializers.UUIDField(source='child.id', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'family_wallet_id', 'child_id', 'created_by',
            'amount', 'transaction_type', 'status',
            'description', 'created_at', 'completed_at'
        ]
        read_only_fields = fields


# Mark multiple transactions as completed
class CompleteTransactionSerializer(serializers.Serializer):
    transaction_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False
    )


# Make Payment With PIN
class MakePaymentSerializer(serializers.Serializer):
    child_id = serializers.UUIDField()
    chore_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pin = serializers.CharField(max_length=4)

    def validate(self, data):
        user = self.context['request'].user
        wallet = FamilyWallet.objects.get(parent=user)

        if not wallet.check_pin(data['pin']):
            raise serializers.ValidationError("Invalid PIN.")

        if wallet.balance < data['amount']:
            raise serializers.ValidationError("Insufficient wallet balance.")

        try:
            child = Child.objects.get(id=data['child_id'], parent=user)
        except Child.DoesNotExist:
            raise serializers.ValidationError("Invalid child.")

        data['wallet'] = wallet
        data['child'] = child
        return data

    def create(self, validated_data):
        from taskmaster.models import Chore

        wallet = validated_data['wallet']
        child = validated_data['child']
        amount = validated_data['amount']
        chore_id = validated_data['chore_id']

        wallet.balance -= amount
        wallet.save()

        txn = Transaction.objects.create(
            parent=wallet.parent,
            child=child,
            chore_id=chore_id,
            amount=amount,
            type='chore_reward',
            status='paid',
            description=f"Reward for chore {chore_id}"
        )
        return txn


# Daily Savings Activity Breakdown
class SavingsActivitySerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.name', read_only=True)
    activity = serializers.CharField(source='chore.title', default="Allowance")
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['child_name', 'activity', 'amount', 'status', 'formatted_date']

    def get_formatted_date(self, obj):
        return obj.created_at.strftime("%d-%B-%Y")


# Dashboard Pie Chart (Saved vs Sent)
class RewardPieChartSerializer(serializers.Serializer):
    saved = serializers.DecimalField(max_digits=10, decimal_places=2)
    sent = serializers.DecimalField(max_digits=10, decimal_places=2)


# Dashboard Bar Chart (Daily High/Low Earners)
class DailyEarningSerializer(serializers.Serializer):
    date = serializers.CharField()
    highest_earner = serializers.CharField()
    highest_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    lowest_earner = serializers.CharField()
    lowest_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


# Wallet & Children Stats Summary
class DashboardStatsSerializer(serializers.Serializer):
    family_wallet_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rewards_sent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rewards_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    children_count = serializers.IntegerField()
    total_children_balance = serializers.DecimalField(max_digits=12, decimal_places=2)


# Allowance Management
class AllowanceSerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(source='parent.id', read_only=True)
    child_id = serializers.UUIDField(source='child.id')

    class Meta:
        model = Allowance
        fields = [
            'id', 'parent_id', 'child_id',
            'amount', 'frequency', 'status',
            'created_at', 'last_paid_at', 'next_payment_date'
        ]
        read_only_fields = ['id', 'parent_id', 'created_at', 'last_paid_at', 'next_payment_date']

    def validate_child_id(self, value):
        user = self.context['request'].user
        try:
            Child.objects.get(id=value, parent=user)
        except Child.DoesNotExist:
            raise serializers.ValidationError("Child not found or does not belong to you.")
        return value

    def create(self, validated_data):
        child = Child.objects.get(id=validated_data.pop('child')['id'])
        allocation = Allowance.objects.create(
            parent=self.context['request'].user,
            child=child,
            **validated_data
        )
        return allocation
