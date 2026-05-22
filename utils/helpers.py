import re
import random
import string
from datetime import datetime


def generate_code(prefix="", length=6):
    """Generate a unique code with optional prefix"""
    chars = string.ascii_uppercase + string.digits
    rand = ''.join(random.choices(chars, k=length))
    if prefix:
        return f"{prefix}-{rand}"
    return rand


def validate_email(email):
    """Validate email format"""
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """Validate phone number (allow digits, +, -, spaces)"""
    if not phone:
        return True
    pattern = r'^[\d\+\-\(\)\s]{7,20}$'
    return bool(re.match(pattern, phone))


def calculate_tax(subtotal, tax_rate):
    """Calculate tax amount"""
    return subtotal * (tax_rate / 100)


def calculate_total(subtotal, tax_amount, discount_amount=0):
    """Calculate total amount"""
    return subtotal + tax_amount - discount_amount
