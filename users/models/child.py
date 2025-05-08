import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from .user import User

class Child(models.Model):
    """
    Model representing a child user associated with a parent.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(User, related_name='children', on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Hashed password
    fullname = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        """
        Set the user's password.
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Check the user's password.
        """
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.username} (Child of {self.parent.fullname})"
