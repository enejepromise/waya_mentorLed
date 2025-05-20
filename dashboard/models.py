from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Child(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(User, related_name='children', on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    pin = models.CharField(max_length=128)  # This will store the hashed 4-digit PIN
    avatar = models.ImageField(upload_to='child_avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_pin(self, raw_pin):
        if not raw_pin.isdigit() or len(raw_pin) != 4:
            raise ValueError("PIN must be exactly 4 digits.")
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)
    def __str__(self):
        return f"{self.username} (Child of {self.parent.fullname})"
