from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

from .utils.email import SendGridEmailService

email_service = SendGridEmailService()

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        email_service.send_parent_welcome(instance.email, instance.fullname)
