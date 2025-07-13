from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.utils import timezone
from children.models import Child

class Goal(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('achieved', 'Achieved'),
    ]

    TROPHY_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    target_duration_months = models.PositiveIntegerField()
    image = models.ImageField(upload_to='goal_images/', blank=True, null=True)
    trophy_image = models.ImageField(upload_to='trophies/', blank=True, null=True)
    trophy_type = models.CharField(max_length=10, choices=TROPHY_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    achieved_at = models.DateTimeField(blank=True, null=True)

    def saved_amount(self):
        # Sum all contributions made toward this goal
        total = self.contributions.aggregate(total=models.Sum('amount'))['total']
        return total or 0

    def percent_completed(self):
        saved = self.saved_amount()
        return min(100, int((saved / self.target_amount) * 100)) if self.target_amount else 0

    def time_remaining(self):
        if self.status == 'achieved':
            return 0
        deadline = self.created_at + timezone.timedelta(days=30 * self.target_duration_months)
        remaining = (deadline - timezone.now()).days
        return max(0, remaining)

    def check_achievement(self):
        if self.status == 'active' and self.saved_amount() >= self.target_amount:
            self.status = 'achieved'
            self.achieved_at = timezone.now()
            # Assign trophy type and image based on percent or amount saved (example logic)
            percent = self.percent_completed()
            if percent >= 100:
                self.trophy_type = 'gold'
                # trophy_image can be set to a static file or generated URL
                self.trophy_image = 'trophies/gold_trophy.png'
            elif percent >= 75:
                self.trophy_type = 'silver'
                self.trophy_image = 'trophies/silver_trophy.png'
            else:
                self.trophy_type = 'bronze'
                self.trophy_image = 'trophies/bronze_trophy.png'
            self.save()
class GoalTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contribution of {self.amount} to {self.goal.title}"
