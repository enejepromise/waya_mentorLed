# utils.py
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, TrackingSettings, ClickTracking
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email(subject, plain_text_message, html_message, to_email):
    """
    Send an email using SendGrid with both plain text and HTML content.

    Args:
        subject (str): Email subject
        plain_text_message (str): Plain text version of the email body
        html_message (str): HTML version of the email body
        to_email (str or list): Recipient email address or list of addresses

    Returns:
        sendgrid.helpers.mail.Response or None: SendGrid response object or None if error occurs
    """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email_obj = To(to_email)  # Supports string or list of emails

        mail = Mail(from_email=from_email, to_email=to_email_obj, subject=subject)

        # Add both plain text and HTML content
        mail.add_content(Content("text/plain", plain_text_message))
        mail.add_content(Content("text/html", html_message))

        # Disable click tracking (optional)
        tracking_settings = TrackingSettings()
        tracking_settings.click_tracking = ClickTracking(enable=False, enable_text=False)
        mail.tracking_settings = tracking_settings

        response = sg.send(mail)
        logger.info(f"Email sent to {to_email} with status code {response.status_code}")
        return response

    except Exception as e:
        logger.error(f"SendGrid error while sending email to {to_email}: {e}", exc_info=True)
        return None


