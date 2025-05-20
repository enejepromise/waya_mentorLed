import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SendGridEmailService:
    def __init__(self):
        self.sender_email = getattr(settings, "SENDGRID_SENDER_EMAIL", None)
        self.api_key = getattr(settings, "SENDGRID_API_KEY", None)

        if not self.sender_email:
            raise ImproperlyConfigured("SENDGRID_SENDER_EMAIL not set in settings.")
        if not self.api_key:
            raise ImproperlyConfigured("SENDGRID_API_KEY not set in settings.")

    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """Send email using SendGrid."""
        message = Mail(
            from_email=self.sender_email,
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            return 200 <= response.status_code < 300  # True if sent successfully
        except Exception as e:
            # You can log this with Sentry or Django logger
            print(f"SendGrid email error: {e}")
            return False

    def send_parent_welcome(self, to_email: str, full_name: str) -> bool:
        subject = "Welcome to Waya!"
        content = f"<p>Dear {full_name},</p><p>Thank you for joining Waya!</p>"
        return self.send_email(to_email, subject, content)

    def send_child_creation_notification(self, to_email: str, child_username: str) -> bool:
        subject = "Your Child Account Has Been Created"
        content = (
            f"<p>Your child account with username <strong>{child_username}</strong> "
            f"has been created successfully.</p>"
        )
        return self.send_email(to_email, subject, content)
