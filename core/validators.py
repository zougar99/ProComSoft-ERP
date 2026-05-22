import re


def validate_required(value, field_name):
    if not value or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"{field_name} is required")
    return value.strip() if isinstance(value, str) else value


def validate_email(email):
    if email:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
    return email


def validate_positive_number(value, field_name):
    if value is not None and value < 0:
        raise ValueError(f"{field_name} must be positive")
    return value
