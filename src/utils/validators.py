"""Input validation utilities."""

import re
from typing import Tuple


def validate_web_name(web_name: str) -> Tuple[bool, str]:
    """
    Validate web name format (URL-safe characters only).

    Args:
        web_name: The web name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not web_name:
        return False, "Web name is required"

    if len(web_name) < 3:
        return False, "Web name must be at least 3 characters"

    if len(web_name) > 100:
        return False, "Web name must be less than 100 characters"

    # Only allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', web_name):
        return False, "Web name can only contain letters, numbers, hyphens, and underscores"

    return True, ""


def validate_domain(domain: str) -> Tuple[bool, str]:
    """
    Validate domain format.

    Args:
        domain: The domain to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain:
        return False, "Domain is required"

    # Basic domain validation pattern
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'

    if not re.match(domain_pattern, domain):
        return False, "Invalid domain format (e.g., example.com)"

    return True, ""


def validate_required_field(value: str, field_name: str, max_length: int = None) -> Tuple[bool, str]:
    """
    Validate a required text field.

    Args:
        value: The value to validate
        field_name: Name of the field (for error messages)
        max_length: Optional maximum length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} is required"

    if max_length and len(value) > max_length:
        return False, f"{field_name} must be less than {max_length} characters"

    return True, ""
