"""
Atmos payment gateway client.
This is a thin wrapper that provides a clean interface but delegates to internal implementation.
"""
import logging
from typing import Dict, Any, Optional, Union

from paytechuz.core.base import BasePaymentGateway
from paytechuz.core.http import HttpClient
from paytechuz.license import validate_api_key
from .internal import AtmosGatewayInternal

logger = logging.getLogger(__name__)


class AtmosGateway(BasePaymentGateway):
    """
    Atmos payment gateway implementation.

    This class provides methods for interacting with the Atmos payment gateway,
    including creating payments, checking payment status, and canceling payments.
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        store_id: str,
        terminal_id: Optional[str] = None,
        is_test_mode: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Atmos gateway.

        Args:
            consumer_key: Atmos consumer key
            consumer_secret: Atmos consumer secret
            store_id: Atmos store ID
            terminal_id: Atmos terminal ID (optional)
            is_test_mode: Whether to use the test environment
            api_key: PayTech API key for license validation (or set PAYTECH_API_KEY env var)
        """
        # Validate license before initializing
        validate_api_key(api_key)
        
        super().__init__(is_test_mode)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.store_id = store_id
        self.terminal_id = terminal_id

        # Base URL is hard coded as per requirements
        self.base_url = 'https://partner.atmos.uz'

        # Initialize HTTP client
        self.client = HttpClient(base_url=self.base_url)

        # Initialize internal implementation
        self._internal = AtmosGatewayInternal(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            store_id=store_id,
            terminal_id=terminal_id,
            is_test_mode=is_test_mode,
            client=self.client
        )

        # Get access token
        self._internal._get_access_token()

    def create_payment(
        self,
        account_id: Union[int, str],
        amount: Union[int, float, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a payment transaction.

        Args:
            account_id: The account ID or order ID
            amount: The payment amount
            **kwargs: Additional parameters

        Returns:
            Dict containing payment details including transaction ID and payment URL
        """
        return self._internal.create_payment(account_id, amount, **kwargs)

    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check payment status.

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
        Cancel payment.

        Args:
            transaction_id: The transaction ID to cancel
            reason: Optional reason for cancellation

        Returns:
            Dict containing cancellation status and details
        """
        return self._internal.cancel_payment(transaction_id, reason)
