"""
PayTechUZ - Unified payment library for Uzbekistan payment systems.

This library provides a unified interface for working with Payme and Click
payment systems in Uzbekistan. It supports Django, Flask, and FastAPI.
"""
from typing import Any

from paytechuz.gateways.payme.client import PaymeGateway
from paytechuz.gateways.click.client import ClickGateway
from paytechuz.core.constants import PaymentGateway

__version__ = '0.1.0'

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
    """
    if gateway_type.lower() == PaymentGateway.PAYME.value:
        return PaymeGateway(**kwargs)
    if gateway_type.lower() == PaymentGateway.CLICK.value:
        return ClickGateway(**kwargs)

    raise ValueError(f"Unsupported gateway type: {gateway_type}")
