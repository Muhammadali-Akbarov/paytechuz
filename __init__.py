"""
PayTechUZ - Unified payment library for Uzbekistan payment systems.

This library provides a unified interface for working with Payme and Click
payment systems in Uzbekistan. It supports Django, Flask, and FastAPI.
"""
from typing import Any, Dict, Optional, Type, Union

from paytechuz.gateways.payme.client import PaymeGateway
from paytechuz.gateways.click.client import ClickGateway
from paytechuz.core.constants import PaymentGateway

__version__ = '0.1.0'

# Import framework integrations
try:
    import django
    has_django = True
except ImportError:
    has_django = False

try:
    import fastapi
    has_fastapi = True
except ImportError:
    has_fastapi = False

try:
    import flask
    has_flask = True
except ImportError:
    has_flask = False


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
