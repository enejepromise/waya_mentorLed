from django.db import models

# Create your models here.
import uuid
from django.db import models
from children.models import Child
from django.utils import timezone


class Task(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_MISSED = 'missed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_MISSED, 'Missed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    assigned_to = models.ForeignKey(Child, related_name='chores', on_delete=models.CASCADE)
    parent = models.ForeignKey('users.User', related_name='chores', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically set completed_at when status changes to completed
        if self.status == self.STATUS_COMPLETED and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != self.STATUS_COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.status}) for {self.assigned_to.username}"
