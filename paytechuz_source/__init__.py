"""
PayTechUZ - Unified payment library for Uzbekistan payment systems.

This library provides a unified interface for working with Payme, Click, and Atmos
payment systems in Uzbekistan. It supports Django, Flask, and FastAPI.
"""

__version__ = '0.3.13'

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


from paytechuz.factory import create_gateway
