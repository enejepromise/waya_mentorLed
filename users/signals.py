from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from .tasks import send_email_task
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    user = reset_password_token.user
    reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{reset_password_token.key}/"
    subject = "Waya Password Reset Request"
    html_content = render_to_string('emails/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
    })
    send_email_task.delay(subject, user.email, html_content)


def send_verification_email(user): 
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email/?uidb64={uid}&token={token}"
    
    subject = "Verify Your Waya Account Email"
    
    html_content = f"""
    <html>
        <body>
            <p>Hello {user.email},</p>
            <p>Thank you for registering with Waya!</p>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verify_url}">Verify Email</a></p>
            <p>If the above link doesn't work, copy and paste the following URL into your browser:</p>
            <p>{verify_url}</p>
            <br>
            <p>Thanks,<br>Waya Team</p>
        </body>
    </html>
    """

    send_email_task.delay(subject, user.email, html_content)
