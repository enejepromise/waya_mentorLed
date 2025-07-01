import uuid
from django.db import models
from django.conf import settings

from django.utils import timezone
from children.models import Child
from users.models import User  


from django.contrib.auth.hashers import make_password, check_password

class FamilyWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.OneToOneField(User, on_delete=models.CASCADE, related_name="family_wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default="Naira")
    pin = models.CharField(max_length=128)  # hashed 4-digit PIN
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_pin(self, raw_pin):
        if not raw_pin.isdigit() or len(raw_pin) != 4:
            raise ValueError("PIN must be exactly 4 digits.")
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)

    def get_total_sent(self):
        return self.transactions.filter(status="paid").aggregate(models.Sum("amount"))["amount__sum"] or 0

    def get_total_pending(self):
        return self.transactions.filter(status="pending").aggregate(models.Sum("amount"))["amount__sum"] or 0

    def __str__(self):
        return f"{self.parent.full_name}'s Wallet - {self.currency}"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("processing", "Processing"),
    ]

    TYPE_CHOICES = [
        ("chore_reward", "Chore Reward"),
        ("allowance_payment", "Allowance Payment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="transactions")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="transactions")
    chore = models.ForeignKey("taskmaster.Chore", null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="chore_reward")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.child.name} - ₦{self.amount}"


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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="allowances")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="allowances")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    last_paid_at = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.child.name} - {self.amount} ({self.frequency})"

    def schedule_next_payment(self):
        if self.frequency == "weekly":
            return self.last_paid_at + timezone.timedelta(weeks=1)
        elif self.frequency == "monthly":
            return self.last_paid_at + timezone.timedelta(days=30)

class ChildWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    savings_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Percentage of each income to be saved automatically"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def earn(self, amount):
        """When the child receives money (chore reward)"""
        savings = amount * (self.savings_rate / 100)
        spendable = amount - savings
        self.balance += spendable
        self.total_earned += amount
        self.save()

    def spend(self, amount):
        """When the child spends money"""
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.total_spent += amount
        self.save()

    def __str__(self):
        return f"{self.child.name}'s Wallet"
