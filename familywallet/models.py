import uuid
from django.core.cache import cache
from users.tasks import sync_wallet_stats_to_dashboard
from decimal import Decimal
from django.db import models, transaction as db_transaction
from django.conf import settings
from django.utils import timezone
from children.models import Child
from users.models import User
from django.contrib.auth.hashers import make_password, check_password

class FamilyWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.OneToOneField(User, on_delete=models.CASCADE, related_name="family_wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default="Naira")
    pin = models.CharField(max_length=128)  # hashed 4-digit PIN
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["created_at"]),
        ]

    def set_pin(self, raw_pin):
        if not raw_pin.isdigit() or len(raw_pin) != 4:
            raise ValueError("PIN must be exactly 4 digits.")
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)

    def add_funds(self, amount: Decimal, description: str, created_by):
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        with db_transaction.atomic():
            self.balance += amount
            self.save()
            transaction_obj = Transaction.objects.create(
                parent=self.parent,
                child=None,
                type='allowance_payment',
                amount=amount,
                description=description,
                status='paid',
                created_at=timezone.now()
            )
            # Invalidate wallet and totals cache for this parent
            self._invalidate_summary_cache()
            sync_wallet_stats_to_dashboard.delay(self.parent_id)
        return transaction_obj

    def create_reward_transaction(self, child, amount: Decimal, description: str):
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient balance.")
        with db_transaction.atomic():
            self.balance -= amount
            self.save()
            transaction_obj = Transaction.objects.create(
                parent=self.parent,
                child=child,
                type='chore_reward',
                amount=amount,
                description=description,
                status='paid',
                created_at=timezone.now()
            )
            # Invalidate wallet and totals cache for this parent
            self._invalidate_summary_cache()
            sync_wallet_stats_to_dashboard.delay(self.parent_id)
        return transaction_obj

    def get_total_sent(self):
        cache_key = f"wallet:total_sent:{self.parent_id}"
        value = cache.get(cache_key)
        if value is not None:
            return value
        value = self.parent.transactions.filter(status="paid").aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal('0.00')
        cache.set(cache_key, value, timeout=60*5)
        return value

    def get_total_pending(self):
        cache_key = f"wallet:total_pending:{self.parent_id}"
        value = cache.get(cache_key)
        if value is not None:
            return value
        value = self.parent.transactions.filter(status="pending").aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal('0.00')
        cache.set(cache_key, value, timeout=60*5)
        return value

    def _invalidate_summary_cache(self):
        """Call after any balance or transaction change for this wallet."""
        cache.delete(f"wallet:total_sent:{self.parent_id}")
        cache.delete(f"wallet:total_pending:{self.parent_id}")
        cache.delete(f"wallet_summary:{self.parent_id}")

    def __str__(self):
        return f"{self.parent.full_name}'s Wallet - {self.currency}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("cancelled", "Cancelled"),
    ]

    TYPE_CHOICES = [
        ("chore_reward", "Chore Reward"),
        ("allowance_payment", "Allowance Payment"),
        ("wallet_funding", "Wallet Funding"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    chore = models.ForeignKey("taskmaster.Chore", null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="chore_reward")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reference = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["child"]),
            models.Index(fields=["status"]),
            models.Index(fields=["type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["parent", "child"]),
            models.Index(fields=["status", "created_at"]),
        ]
        ordering = ["-created_at"]

    def complete_transaction(self):
        if self.status != 'pending':
            raise ValueError("Only pending transactions can be completed.")
        self.status = 'paid'
        self.completed_at = timezone.now()
        self.save()
        # Invalidate parent wallet totals if this is a reward/payout
        if hasattr(self.parent, 'family_wallet'):
            self.parent.family_wallet._invalidate_summary_cache()

    def cancel_transaction(self):
        if self.status not in ['pending', 'processing']:
            raise ValueError("Only pending or processing transactions can be cancelled.")
        self.status = 'cancelled'
        self.save()
        # Invalidate on status change
        if hasattr(self.parent, 'family_wallet'):
            self.parent.family_wallet._invalidate_summary_cache()

    def __str__(self):
        child_name = self.child.name if self.child else "No Child"
        return f"{self.type} - {child_name} - ₦{self.amount}"

class Allowance(models.Model):
    FREQUENCY_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("pending", "Pending"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="allowances", db_index=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="allowances", db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_paid_at = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["child"]),
            models.Index(fields=["status"]),
            models.Index(fields=["frequency"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["parent", "child"]),
        ]

    def __str__(self):
        return f"{self.child.name} - {self.amount} ({self.frequency})"

    def schedule_next_payment(self):
        if self.last_paid_at is None:
            return None
        if self.frequency == "weekly":
            return self.last_paid_at + timezone.timedelta(weeks=1)
        elif self.frequency == "monthly":
            return self.last_paid_at + timezone.timedelta(days=30)
        return None

class ChildWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name="wallet", db_index=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    savings_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text="Percentage of each income to be saved automatically"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def earn(self, amount: Decimal):
        savings = amount * (self.savings_rate / Decimal('100'))
        spendable = amount - savings
        self.balance += spendable
        self.total_earned += amount
        self.save()
        self._invalidate_cache()

    def spend(self, amount: Decimal):
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.total_spent += amount
        self.save()
        self._invalidate_cache()

    def get_summary(self):
        """Cached summary for child wallet - balance, earned, spent"""
        cache_key = f"child_wallet_summary:{self.child_id}"
        summary = cache.get(cache_key)
        if summary:
            return summary
        summary = {
            "balance": self.balance,
            "total_earned": self.total_earned,
            "total_spent": self.total_spent,
        }
        cache.set(cache_key, summary, timeout=60*5)
        return summary

    def _invalidate_cache(self):
        cache.delete(f"child_wallet_summary:{self.child_id}")

    def __str__(self):
        return f"{self.child.name}'s Wallet"
