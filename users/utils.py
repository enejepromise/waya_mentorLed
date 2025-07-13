import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, TrackingSettings, ClickTracking
from django.conf import settings

def send_email(subject, message, to_email):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

        # Correct: use to_emails, not to_email
        email = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,  # ✅ This is correct
            subject=subject,
            plain_text_content=message
        )

        # Disable click tracking (optional)
        tracking_settings = TrackingSettings()
        tracking_settings.click_tracking = ClickTracking(enable=False, enable_text=False)
        email.tracking_settings = tracking_settings

        response = sg.send(email)
        return response

    except Exception as e:
        print(f"Failed to send verification email to {to_email}: {str(e)}")
        raise
