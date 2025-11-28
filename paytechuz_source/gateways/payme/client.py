"""
Payme payment gateway client.
This is a thin wrapper that provides a clean interface but delegates to internal implementation.
"""
import logging
from typing import Dict, Any, Optional, Union

from paytechuz.core.base import BasePaymentGateway
from paytechuz.core.http import HttpClient
from paytechuz.core.constants import PaymeNetworks
from paytechuz.core.utils import handle_exceptions
from paytechuz.license import validate_api_key

from .cards import PaymeCards
from .receipts import PaymeReceipts
from .internal import PaymeGatewayInternal

logger = logging.getLogger(__name__)


class PaymeGateway(BasePaymentGateway):
    """
    Payme payment gateway implementation.

    This class provides methods for interacting with the Payme payment gateway,
    including creating payments, checking payment status, and canceling payments.
    """

    def __init__(
        self,
        payme_id: str,
        payme_key: Optional[str] = None,
        fallback_id: Optional[str] = None,
        is_test_mode: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Payme gateway.

        Args:
            payme_id: Payme merchant ID
            payme_key: Payme merchant key for authentication
            fallback_id: Fallback merchant ID
            is_test_mode: Whether to use the test environment
            api_key: PayTech API key for license validation (or set PAYTECH_API_KEY env var)
        """
        # Validate license before initializing
        validate_api_key(api_key)
        
        super().__init__(is_test_mode)
        self.payme_id = payme_id
        self.payme_key = payme_key
        self.fallback_id = fallback_id

        # Set the API URL based on the environment
        url = PaymeNetworks.TEST_NET if is_test_mode else PaymeNetworks.PROD_NET

        # Initialize HTTP client
        self.http_client = HttpClient(base_url=url)

        # Initialize components
        self.cards = PaymeCards(http_client=self.http_client, payme_id=payme_id)
        self.receipts = PaymeReceipts(
            http_client=self.http_client,
            payme_id=payme_id,
            payme_key=payme_key
        )

        # Initialize internal implementation
        self._internal = PaymeGatewayInternal(
            payme_id=payme_id,
            payme_key=payme_key,
            fallback_id=fallback_id,
            is_test_mode=is_test_mode,
            http_client=self.http_client,
            cards=self.cards,
            receipts=self.receipts
        )

    def generate_pay_link(
        self,
        id: Union[int, str],
        amount: Union[int, float, str],
        return_url: str,
        account_field_name: str = "order_id"
    ) -> str:
        """
        Generate a payment link for a specific order.

        Parameters
        ----------
        id : Union[int, str]
            Unique identifier for the account/order.
        amount : Union[int, float, str]
            Payment amount in som.
        return_url : str
            URL to redirect after payment completion.
        account_field_name : str, optional
            Field name for account identifier (default: "order_id").

        Returns
        -------
        str
            Payme checkout URL with encoded parameters.

        References
        ----------
        https://developer.help.paycom.uz/initsializatsiya-platezhey/
        """
        return self._internal.generate_pay_link(id, amount, return_url, account_field_name)

    async def generate_pay_link_async(
        self,
        id: Union[int, str],
        amount: Union[int, float, str],
        return_url: str,
        account_field_name: str = "order_id"
    ) -> str:
        """
        Async version of generate_pay_link.

        Parameters
        ----------
        id : Union[int, str]
            Unique identifier for the account/order.
        amount : Union[int, float, str]
            Payment amount in som.
        return_url : str
            URL to redirect after payment completion.
        account_field_name : str, optional
            Field name for account identifier (default: "order_id").

        Returns
        -------
        str
            Payme checkout URL with encoded parameters.
        """
        return self.generate_pay_link(id, amount, return_url, account_field_name)

    @handle_exceptions
    def create_payment(
        self,
        id: Union[int, str],
        amount: Union[int, float, str],
        return_url: str = "",
        account_field_name: str = "order_id"
    ) -> str:
        """
        Create a payment using Payme.

        Args:
            amount: Payment amount in som
            account_id: Account or order ID
            return_url: Return URL after payment (default: "")
            account_field_name: Field name for account ID (default: "order_id")

        Returns:
            str: Payme payment URL
        """
        return self.generate_pay_link(id, amount, return_url, account_field_name)

    @handle_exceptions
    async def create_payment_async(
        self,
        id: Union[int, str],
        amount: Union[int, float, str],
        return_url: str = "",
        account_field_name: str = "order_id"
    ) -> str:
        """
        Async version of create_payment.

        Args:
            amount: Payment amount in som
            account_id: Account or order ID
            return_url: Return URL after payment (default: "")
            account_field_name: Field name for account ID (default: "order_id")

        Returns:
            str: Payme payment URL
        """
        return await self.generate_pay_link_async(id, amount, return_url, account_field_name)

    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check payment status using Payme receipts.

        Args:
            transaction_id: The receipt ID to check

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
        Cancel payment using Payme receipts.

        Args:
            transaction_id: The receipt ID to cancel
            reason: Optional reason for cancellation

        Returns:
            Dict containing cancellation status and details
        """
        return self._internal.cancel_payment(transaction_id, reason)
