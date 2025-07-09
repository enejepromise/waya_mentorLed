# utils.py
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, TrackingSettings, ClickTracking
from django.conf import settings

def send_email(subject, message, to_email):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

    from_email = Email(settings.DEFAULT_FROM_EMAIL)
    to_email = To(to_email)
    content = Content("text/plain", message)

    mail = Mail(from_email=from_email, to_email=to_email, subject=subject)
    mail.add_content(content)

    # Disable click tracking (optional)
    tracking_settings = TrackingSettings()
    tracking_settings.click_tracking = ClickTracking(enable=False, enable_text=False)
    mail.tracking_settings = tracking_settings

    response = sg.send(mail)
    return response

