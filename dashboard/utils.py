import hashlib

def make_pin(pin: str) -> str:
    """
    Hashes a 4-digit PIN using SHA-256.

    Args:
        pin (str): The raw 4-digit PIN.

    Returns:
        str: A hashed version of the PIN.
    """
    return hashlib.sha256(pin.encode()).hexdigest()


def verify_pin(raw_pin: str, hashed_pin: str) -> bool:
    """
    Verifies a raw 4-digit PIN against its hashed version.

    Args:
        raw_pin (str): The PIN entered by the user.
        hashed_pin (str): The hashed version stored in the database.

    Returns:
        bool: True if the PIN matches, False otherwise.
    """
    return make_pin(raw_pin) == hashed_pin
