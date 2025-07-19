import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from users.models import User

class Child(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    parent = models.ForeignKey(
        User,
        related_name='children',
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.ROLE_PARENT},
        db_index=True
    )

    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255, default='Unknown')
    pin = models.CharField(max_length=128)  # Hashed PIN
    avatar = models.ImageField(upload_to='child_avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    db_index=True

    def set_pin(self, raw_pin):
        if not raw_pin.isdigit() or len(raw_pin) != 4:
            raise ValueError("PIN must be exactly 4 digits.")
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)
    

    def save(self, *args, **kwargs):
        if not self.pin:
            raise ValueError("PIN must be set before saving a new child.")
        if not self.pin.startswith('pbkdf2_'):
            self.set_pin(self.pin)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if not self.username.isalnum():
            raise ValidationError("Username must be alphanumeric.")

    class Meta:
        ordering = ['-created_at']
        indexes = [  
            models.Index(fields=['parent']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return f"{self.username} (Child of {self.parent.full_name})"

    @property
    def pk(self):
        return self.id

    @property
    def is_authenticated(self):
        return True
