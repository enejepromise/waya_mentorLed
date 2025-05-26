from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password

def generate_uid_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token

def make_pin(raw_pin: str) -> str:
    """
    Hash a PIN or password using Django's make_password.
    """
    return make_password(raw_pin)
