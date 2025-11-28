"""
Click payment gateway client.
This is a thin wrapper that provides a clean interface but delegates to internal implementation.
"""
import logging
from typing import Dict, Any, Optional, Union

from paytechuz.core.base import BasePaymentGateway
from paytechuz.core.http import HttpClient
from paytechuz.core.constants import ClickNetworks
from paytechuz.license import validate_api_key
from .merchant import ClickMerchantApi
from .internal import ClickGatewayInternal

logger = logging.getLogger(__name__)


class ClickGateway(BasePaymentGateway):
    """
    Click payment gateway implementation.

    This class provides methods for interacting with the Click payment gateway,
    including creating payments, checking payment status, and canceling payments.
    """

    def __init__(
        self,
        service_id: str,
        merchant_id: str,
        merchant_user_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        is_test_mode: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Click gateway.

        Args:
            service_id: Click service ID
            merchant_id: Click merchant ID
            merchant_user_id: Click merchant user ID
            secret_key: Secret key for authentication
            is_test_mode: Whether to use the test environment
            api_key: PayTech API key for license validation (or set PAYTECH_API_KEY env var)
        """
        # Validate license before initializing
        validate_api_key(api_key)
        
        super().__init__(is_test_mode)
        self.service_id = service_id
        self.merchant_id = merchant_id
        self.merchant_user_id = merchant_user_id
        self.secret_key = secret_key

        # Set the API URL based on the environment
        url = ClickNetworks.TEST_NET if is_test_mode else ClickNetworks.PROD_NET

        # Initialize HTTP client
        self.http_client = HttpClient(base_url=url)

        # Initialize merchant API
        self.merchant_api = ClickMerchantApi(
            http_client=self.http_client,
            service_id=service_id,
            merchant_user_id=merchant_user_id,
            secret_key=secret_key
        )

        # Initialize internal implementation
        self._internal = ClickGatewayInternal(
            service_id=service_id,
            merchant_id=merchant_id,
            merchant_user_id=merchant_user_id,
            secret_key=secret_key,
            is_test_mode=is_test_mode,
            http_client=self.http_client,
            merchant_api=self.merchant_api
        )

    def create_payment(
        self,
        id: Union[int, str],
        amount: Union[int, float, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a payment using Click.

        Args:
            amount: The payment amount in som
            id: The account ID or order ID
            **kwargs: Additional parameters for the payment
                - description: Payment description
                - return_url: URL to return after payment
                - callback_url: URL for payment notifications
                - language: Language code (uz, ru, en)
                - phone: Customer phone number
                - email: Customer email

        Returns:
            Dict containing payment details including transaction ID and payment URL
        """
        return self._internal.create_payment(id, amount, **kwargs)

    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check payment status using Click merchant API.

        Args:
            transaction_id: The transaction ID to check

        Returns:
            Dict containing payment status and details
        """
        return self._internal.check_payment(transaction_id)

    def cancel_payment(
        self,
        transaction_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel payment using Click merchant API.

        Args:
            transaction_id: The transaction ID to cancel
            reason: Optional reason for cancellation

        Returns:
            Dict containing cancellation status and details
        """
        return self._internal.cancel_payment(transaction_id, reason)

    def card_token_request(
        self,
        card_number: str,
        expire_date: str,
        temporary: int = 0
    ) -> Dict[str, Any]:
        """
        Request a card token for card payment.

        Args:
            card_number: Card number (e.g., "5614681005030279")
            expire_date: Card expiration date (e.g., "0330" for March 2030)
            temporary: Whether the token is temporary (0 or 1)

        Returns:
            Dict containing card token and related information
        """
        return self._internal.card_token_request(card_number, expire_date, temporary)

    def card_token_verify(
        self,
        card_token: str,
        sms_code: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Verify a card token with SMS code.

        Args:
            card_token: Card token from card_token_request
            sms_code: SMS code sent to the card holder

        Returns:
            Dict containing verification status and card information
        """
        return self._internal.card_token_verify(card_token, sms_code)

    def card_token_payment(
        self,
        card_token: str,
        amount: Union[int, float],
        transaction_parameter: str
    ) -> Dict[str, Any]:
        """
        Make a payment using a verified card token.

        Args:
            card_token: Verified card token
            amount: Payment amount in som
            transaction_parameter: Unique transaction parameter

        Returns:
            Dict containing payment status and payment ID
        """
        return self._internal.card_token_payment(card_token, amount, transaction_parameter)
