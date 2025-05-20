from django.db.models.signals import post_save
from django.dispatch import receiver
from users.utils.email import SendGridEmailService

email_service = SendGridEmailService()

@receiver(post_save)
def send_child_creation_email(sender, instance, created, **kwargs):
    # Delayed import to avoid circular import
    from dashboard.models import Child

    if sender is Child and created:
        email_service.send_child_creation_notification(
            instance.parent.email, instance.username
        )
