import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password


class UserManager(BaseUserManager):
    """
    Custom user manager to handle user creation for parent and child roles.
    """

    def create_user(self, email, full_name, role, password=None, **extra_fields):
        """
        Create and return a user with email, full_name, role, and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        if role not in ['parent', 'child']:
            raise ValueError("Role must be either 'parent' or 'child'")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """
        Create and return a superuser with elevated permissions.
        """
        extra_fields.setdefault('role', 'parent')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, 'parent', password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for both parents and children.
    Parents register via email/password.
    Children are created under a parent and login with username & PIN.
    """

    ROLE_PARENT = 'parent'
    ROLE_CHILD = 'child'

    ROLE_CHOICES = [
        (ROLE_PARENT, 'Parent'),
        (ROLE_CHILD, 'Child'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)  # Allow blank for children if needed
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    terms_accepted = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    def clean(self):
        # Enforce email required only for parents
        if self.role == self.ROLE_PARENT:
            if not self.email:
                raise ValidationError("Parent users must have an email address.")
            if not self.terms_accepted:
                raise ValidationError("Parent users must accept the Terms and Conditions.")

        if self.role == self.ROLE_CHILD and self.email:
            # Optionally prevent children from having emails if you want
            pass

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.role})"

class Child(models.Model):
    """
    Child model linked to a parent user.
    Children login with username and 4-digit PIN.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(User, related_name='children', on_delete=models.CASCADE, limit_choices_to={'role': User.ROLE_PARENT})
    username = models.CharField(max_length=150, unique=True)
    pin = models.CharField(max_length=128)  # Stores hashed 4-digit PIN
    avatar = models.ImageField(upload_to='child_avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_pin(self, raw_pin):
        """
        Validate and hash the PIN before saving.
        """
        if not raw_pin.isdigit() or len(raw_pin) != 4:
            raise ValueError("PIN must be exactly 4 digits.")
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        """
        Check the raw PIN against the stored hashed PIN.
        """
        return check_password(raw_pin, self.pin)

    def __str__(self):
        return f"{self.username} (Child of {self.parent.full_name})"

    class Meta:
        ordering = ['username']
        verbose_name = 'Child'
        verbose_name_plural = 'Children'