"""
PayTechUZ - Unified payment library for Uzbekistan payment systems.

This library provides a unified interface for working with Payme, Click, and Atmos
payment systems in Uzbekistan. It supports Django, Flask, and FastAPI.
"""

__version__ = '0.3.7'

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

from paytechuz.core.base import BasePaymentGateway  # noqa: E402
from paytechuz.gateways.payme.client import PaymeGateway  # noqa: E402
from paytechuz.gateways.click.client import ClickGateway  # noqa: E402
from paytechuz.gateways.atmos.client import AtmosGateway  # noqa: E402
from paytechuz.core.constants import PaymentGateway  # noqa: E402


def create_gateway(gateway_type: str, **kwargs) -> BasePaymentGateway:
    """
    Create a payment gateway instance.

    Args:
        gateway_type: Type of gateway ('payme', 'click', or 'atmos')
        **kwargs: Gateway-specific configuration

    Returns:
        Payment gateway instance

    Raises:
        ValueError: If the gateway type is not supported
        ImportError: If the required gateway module is not available
    """
    if gateway_type.lower() == PaymentGateway.PAYME.value:
        return PaymeGateway(**kwargs)
    if gateway_type.lower() == PaymentGateway.CLICK.value:
        return ClickGateway(**kwargs)
    if gateway_type.lower() == PaymentGateway.ATMOS.value:
        return AtmosGateway(**kwargs)

    raise ValueError(f"Unsupported gateway type: {gateway_type}")
