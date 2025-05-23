from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings

@shared_task
def send_email_task(subject, message, recipient_email):
    """
    Async task to send email.
    """
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    email.send(fail_silently=False)
