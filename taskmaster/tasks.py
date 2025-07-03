from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_verification_email_async(subject, message, recipient_list):
    """
    Send verification email asynchronously.
    Typically used during chore app signup or parent email verification.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )


@shared_task
def send_chore_email(subject, recipient_email, message):
    """
    Send chore-related notification email (when a child completes a chore).

    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )