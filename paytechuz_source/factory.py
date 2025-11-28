from paytechuz.core.base import BasePaymentGateway
from paytechuz.gateways.payme.client import PaymeGateway
from paytechuz.gateways.click.client import ClickGateway
from paytechuz.gateways.atmos.client import AtmosGateway
from paytechuz.core.constants import PaymentGateway
from paytechuz.license import validate_api_key

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
        UnknownPartnerError: If the license check fails
    """
    # Validate license before creating gateway
    # Check if api_key is passed in kwargs, otherwise it will check env var
    api_key = kwargs.get('api_key')
    validate_api_key(api_key)

    if gateway_type.lower() == PaymentGateway.PAYME.value:
        return PaymeGateway(**kwargs)
    if gateway_type.lower() == PaymentGateway.CLICK.value:
        return ClickGateway(**kwargs)
    if gateway_type.lower() == PaymentGateway.ATMOS.value:
        return AtmosGateway(**kwargs)

    raise ValueError(f"Unsupported gateway type: {gateway_type}")
