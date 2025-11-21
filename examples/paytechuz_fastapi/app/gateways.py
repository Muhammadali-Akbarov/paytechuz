from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.atmos import AtmosGateway

from app import config


def get_gateways(name=None):
    """
    Get payment gateway(s).

    Args:
        name: Gateway name ('payme', 'click', or 'atmos').
              If None, returns all gateways.

    Returns:
        Single gateway instance if name is provided,
        or dict of all gateways if name is None.
    """
    if name:
        if name == "payme":
            return PaymeGateway(
                payme_id=config.PAYME_ID,
                payme_key=config.PAYME_KEY,
                is_test_mode=config.IS_TEST_MODE
            )
        if name == "click":
            return ClickGateway(
                service_id=config.CLICK_SERVICE_ID,
                merchant_id=config.CLICK_MERCHANT_ID,
                merchant_user_id=config.CLICK_MERCHANT_USER_ID,
                secret_key=config.CLICK_SECRET_KEY,
                is_test_mode=config.IS_TEST_MODE
            )
        if name == "atmos":
            return AtmosGateway(
                consumer_key=config.ATMOS_CONSUMER_KEY,
                consumer_secret=config.ATMOS_CONSUMER_SECRET,
                store_id=config.ATMOS_STORE_ID,
                terminal_id=config.ATMOS_TERMINAL_ID,
                is_test_mode=config.IS_TEST_MODE
            )

        return None

    return {
        "payme": PaymeGateway(
            payme_id=config.PAYME_ID,
            payme_key=config.PAYME_KEY,
            is_test_mode=config.IS_TEST_MODE
        ),
        "click": ClickGateway(
            service_id=config.CLICK_SERVICE_ID,
            merchant_id=config.CLICK_MERCHANT_ID,
            merchant_user_id=config.CLICK_MERCHANT_USER_ID,
            secret_key=config.CLICK_SECRET_KEY,
            is_test_mode=config.IS_TEST_MODE
        ),
        "atmos": AtmosGateway(
            consumer_key=config.ATMOS_CONSUMER_KEY,
            consumer_secret=config.ATMOS_CONSUMER_SECRET,
            store_id=config.ATMOS_STORE_ID,
            terminal_id=config.ATMOS_TERMINAL_ID,
            is_test_mode=config.IS_TEST_MODE
        )
    }
