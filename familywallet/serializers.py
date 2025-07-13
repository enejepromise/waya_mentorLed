from rest_framework import serializers
from decimal import Decimal
from .models import FamilyWallet, ChildWallet, Transaction, Allowance
from children.models import Child
from django.db import transaction as db_transaction


# Family Wallet Serializer
class FamilyWalletSerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(source='parent.id', read_only=True)

    class Meta:
        model = FamilyWallet
        fields = ['id', 'parent_id', 'balance', 'currency', 'updated_at']
        read_only_fields = fields


# Add Funds Serializer
class AddFundsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(max_length=255)

    def validate_amount(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Amount must be positive.")
        return value

class PaystackPaymentInitSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

class PaystackPaymentVerifySerializer(serializers.Serializer):
    reference = serializers.CharField()

    def validate_reference(self, value):
        if not value.strip():
            raise serializers.ValidationError("Reference is required.")
        return value

# Wallet PIN Serializer
class WalletPinSerializer(serializers.Serializer):
    pin = serializers.CharField(min_length=4, max_length=4)

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must be exactly 4 digits.")
        return value


# Child Wallet Serializer
class ChildWalletSerializer(serializers.ModelSerializer):
    child_id = serializers.UUIDField(source='child.id')  
    child_name = serializers.CharField(source='child.name')  
    class Meta:
        model = ChildWallet
        fields = ['id', 'child_name', 'balance', 'total_earned', 'total_spent', 'savings_rate']

# Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
    family_wallet_id = serializers.UUIDField(source='parent.family_wallet.id', read_only=True)
    child_id = serializers.UUIDField(source='child.id') 
    child_name = serializers.CharField(source='child.name', read_only=True)
    class Meta:
        model = Transaction
        fields = [
            'id', 'family_wallet_id','child_id', 
            'child_name',
            'type', 'amount', 'status',
            'description', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'family_wallet_id', 'created_at', 'completed_at']

    def create(self, validated_data):
        child_id = validated_data.pop('child')['id'] if 'child' in validated_data else validated_data.pop('child_id', None)
        child = Child.objects.get(id=child_id)
        validated_data['child'] = child
        # Set parent from request user to avoid null parent_id
        validated_data['parent'] = self.context['request'].user
        return super().create(validated_data)

# Complete Multiple Transactions Serializer
class CompleteTransactionSerializer(serializers.Serializer):
    transaction_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False
    )

# Make Payment Serializer
class MakePaymentSerializer(serializers.Serializer):
    child_id = serializers.UUIDField()
    chore_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    pin = serializers.CharField(max_length=4)

    def validate(self, data):
        user = self.context['request'].user
        try:
            wallet = FamilyWallet.objects.get(parent=user)
        except FamilyWallet.DoesNotExist:
            raise serializers.ValidationError("Family wallet not found.")

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
        wallet = validated_data['wallet']
        child = validated_data['child']
        amount = validated_data['amount']
        chore_id = validated_data['chore_id']

        # Deduct balance and create transaction atomically
        with db_transaction.atomic():
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


# Savings Activity Breakdown Serializer
class SavingsActivitySerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.name')
    child_id = serializers.UUIDField(source='child.id')
    activity = serializers.CharField(source='chore.title', default="Allowance")
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['child_name', 'activity', 'amount', 'status', 'formatted_date']

    def get_formatted_date(self, obj):
        return obj.created_at.strftime("%d-%B-%Y")


# Reward Pie Chart Serializer
class RewardPieChartSerializer(serializers.Serializer):
    saved = serializers.DecimalField(max_digits=12, decimal_places=2)
    sent = serializers.DecimalField(max_digits=12, decimal_places=2)


# Daily Earning Bar Chart Serializer
class DailyEarningSerializer(serializers.Serializer):
    date = serializers.CharField()
    highest_earner = serializers.CharField()
    highest_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    lowest_earner = serializers.CharField()
    lowest_amount = serializers.DecimalField(max_digits=12, decimal_places=2)


# Dashboard Stats Serializer
class DashboardStatsSerializer(serializers.Serializer):
    family_wallet_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rewards_sent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rewards_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    children_count = serializers.IntegerField()
    total_children_balance = serializers.DecimalField(max_digits=12, decimal_places=2)

# Allowance Serializer
class AllowanceSerializer(serializers.ModelSerializer):
    # parent_id is read-only, only shown in response
    parent_id = serializers.UUIDField(source='parent.id', read_only=True)
    
    # write-only: client provides this UUID to assign the child
    child_id = serializers.UUIDField()

    # optional: include a read-only name of the child to show in response
    child_name = serializers.CharField(source='child.name')

    class Meta:
        model = Allowance
        fields = [
            'id', 'parent_id', 'child_id', 'child_name',
            'amount', 'frequency', 'status',
            'created_at', 'last_paid_at', 'next_payment_date'
        ]
        read_only_fields = [
            'id', 'parent_id',
            'created_at', 'last_paid_at', 'next_payment_date'
        ]

    def validate_child_id(self, value):
        """
        Ensure the child exists and belongs to the authenticated parent.
        """
        user = self.context['request'].user
        if not Child.objects.filter(id=value, parent=user).exists():
            raise serializers.ValidationError("Child not found or does not belong to you.")
        return value

    def create(self, validated_data):
        """
        Replace child_id with the actual child instance before saving.
        """
        child_id = validated_data.pop('child_id')
        child = Child.objects.get(id=child_id)
        validated_data['child'] = child
        validated_data['parent'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Handle updates safely: map child_id to child, if provided.
        """
        child_id = validated_data.pop('child_id', None)
        if child_id:
            child = Child.objects.get(id=child_id)
            validated_data['child'] = child
        return super().update(instance, validated_data)
