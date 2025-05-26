from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


@shared_task
def send_email_task(subject, to_email, html_content):
    message = Mail(
        from_email=settings.SENDGRID_SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        # Log error in production
        print(f"SendGrid error: {e}")
        return None
