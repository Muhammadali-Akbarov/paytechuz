"""PayTechUZ - Unified payment library for Uzbekistan payment systems.

This library provides a unified interface for working with Payme and Click
payment systems in Uzbekistan. It supports Django, Flask, and FastAPI.
"""
from typing import Any

__version__ = '0.1.4'


# Define dummy classes to avoid import errors
class PaymeGateway:
    """Dummy PaymeGateway class to avoid import errors."""
    def __init__(self, **kwargs):
        pass


class ClickGateway:
    """Dummy ClickGateway class to avoid import errors."""
    def __init__(self, **kwargs):
        pass


class PaymentGateway:
    """Dummy PaymentGateway enum to avoid import errors."""
    class PAYME:
        value = 'payme'

    class CLICK:
        value = 'click'


# Import framework integrations - these imports are used to check availability
# of frameworks, not for direct usage
try:
    import django  # noqa: F401 - Used for availability check
    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

try:
    import fastapi  # noqa: F401 - Used for availability check
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

try:
    import flask  # noqa: F401 - Used for availability check
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


def create_gateway(gateway_type: str, **kwargs) -> Any:
    """
    Create a payment gateway instance.

    Args:
        gateway_type: Type of gateway ('payme' or 'click')
        **kwargs: Gateway-specific configuration

    Returns:
        Payment gateway instance

    Raises:
        ValueError: If the gateway type is not supported
        ImportError: If the required gateway module is not available
    """
    # Just use the dummy classes for now
    if gateway_type.lower() == 'payme':
        return PaymeGateway(**kwargs)
    if gateway_type.lower() == 'click':
        return ClickGateway(**kwargs)

    raise ValueError(f"Unsupported gateway type: {gateway_type}")
