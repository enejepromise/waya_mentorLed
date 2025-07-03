from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from users.models import User


class Child(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        User,
        related_name='children',
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.ROLE_PARENT}  # Ensures only parents can be assigned as parent
    )
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255, default='Unknown')      
    pin = models.CharField(max_length=128)  # Stores hashed 4-digit PIN
    avatar = models.ImageField(upload_to='child_avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_pin(self, raw_pin):
        if not raw_pin.isdigit() or len(raw_pin) != 4:
            raise ValueError("PIN must be exactly 4 digits.")
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)

    def save(self, *args, **kwargs):
        if not self.pk and not self.pin:
            raise ValueError("PIN must be set before saving a new child.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} (Child of {self.parent.full_name})"