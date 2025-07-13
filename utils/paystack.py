# utils/paystack.py
import requests
from django.conf import settings

def initialize_payment(email, amount, reference, callback_url=None):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": int(amount * 100),  # Convert to kobo
        "reference": reference,
    }
    if callback_url:
        data["callback_url"] = callback_url

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def verify_payment(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(url, headers=headers)
    return response.json()
