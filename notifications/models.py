from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Notification(models.Model):
    TYPE_CHOICES = [
        ('task_completed', 'Task Completed'),
        ('reward_requested', 'Reward Requested'),
        ('chore_reminder', 'Chore Reminder'),
        ('weekly_summary', 'Weekly Summary'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    related_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} → {self.parent.username}"


class Reward(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="reward")
    reward_approval_required = models.BooleanField(default=False)
    max_daily_reward = models.PositiveIntegerField(default=0)
    allow_savings = models.BooleanField(default=True)

    def __str__(self):
        return f"Reward for {self.user.full_name if hasattr(self.user, 'full_name') else self.user.email}"