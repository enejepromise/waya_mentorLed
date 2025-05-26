from django.core.mail import EmailMessage
from django.conf import settings

def send_email(subject, message, recipient_email):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    email.send()
