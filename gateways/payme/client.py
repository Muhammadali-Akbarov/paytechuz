"""
Payme payment gateway client.
"""
import logging
from typing import Dict, Any, Optional, Union

from paytechuz.core.base import BasePaymentGateway
from paytechuz.core.http import HttpClient
from paytechuz.core.constants import PaymeNetworks
from paytechuz.core.utils import format_amount, handle_exceptions
from paytechuz.gateways.payme.cards import PaymeCards
from paytechuz.gateways.payme.receipts import PaymeReceipts

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
        is_test_mode: bool = False
    ):
        """
        Initialize the Payme gateway.

        Args:
            payme_id: Payme merchant ID
            payme_key: Payme merchant key for authentication
            fallback_id: Fallback merchant ID
            is_test_mode: Whether to use the test environment
        """
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

    @handle_exceptions
    def create_payment(
        self,
        amount: Union[int, float, str],
        account_id: Union[int, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a payment using Payme receipts.

        Args:
            amount: The payment amount in som
            account_id: The account ID or order ID
            **kwargs: Additional parameters for the payment
                - description: Payment description
                - detail: Payment details
                - callback_url: URL to redirect after payment
                - return_url: URL to return after payment
                - phone: Customer phone number
                - email: Customer email
                - language: Language code (uz, ru, en)
                - expire_minutes: Payment expiration time in minutes

        Returns:
            Dict containing payment details including transaction ID and payment URL
        """
        # Format amount to tiyin (1 som = 100 tiyin)
        amount_tiyin = format_amount(amount)

        # Extract additional parameters
        description = kwargs.get('description', f'Payment for account {account_id}')
        detail = kwargs.get('detail', {})
        callback_url = kwargs.get('callback_url')
        return_url = kwargs.get('return_url')
        phone = kwargs.get('phone')
        email = kwargs.get('email')
        language = kwargs.get('language', 'uz')
        expire_minutes = kwargs.get('expire_minutes', 60)  # Default 1 hour

        # Check if we have a merchant key
        if self.payme_key:
            # Create receipt using the API
            receipt_data = self.receipts.create(
                amount=amount_tiyin,
                account={"account_id": str(account_id)},
                description=description,
                detail=detail,
                callback_url=callback_url,
                return_url=return_url,
                phone=phone,
                email=email,
                language=language,
                expire_minutes=expire_minutes
            )

            # Extract receipt ID and payment URL
            receipt_id = receipt_data.get('receipt', {}).get('_id')
            payment_url = receipt_data.get('receipt', {}).get('pay_url')

            return {
                'transaction_id': receipt_id,
                'payment_url': payment_url,
                'amount': amount,
                'account_id': account_id,
                'status': 'created',
                'raw_response': receipt_data
            }
        else:
            # Generate a payment URL using payme-pkg style
            # This is a fallback method that doesn't require authentication
            import base64
            from paytechuz.core.utils import generate_id

            # Generate a unique transaction ID
            transaction_id = generate_id("payme")

            # Format amount to the smallest currency unit (tiyin)
            # amount_tiyin is already in tiyin format

            # Build the payment parameters string
            # Format: m=merchant_id;ac.field=value;a=amount;c=callback_url
            params_str = f"m={self.payme_id};ac.id={account_id};a={amount_tiyin}"

            # Add callback URL if provided (this is used for return URL in payme-pkg)
            if return_url:
                params_str += f";c={return_url}"

            # Encode the parameters string to base64
            encoded_params = base64.b64encode(params_str.encode("utf-8")).decode("utf-8")

            # Build the payment URL
            if self.is_test_mode:
                payment_url = f"https://test.paycom.uz/{encoded_params}"
            else:
                payment_url = f"https://checkout.paycom.uz/{encoded_params}"

            # Print the parameters for debugging
            print("Payme payment parameters:")
            print(f"Parameters string: {params_str}")
            print(f"Encoded parameters: {encoded_params}")
            print(f"Payment URL: {payment_url}")

            return {
                'transaction_id': transaction_id,
                'payment_url': payment_url,
                'amount': amount,
                'account_id': account_id,
                'status': 'created',
                'raw_response': {}
            }

    @handle_exceptions
    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check payment status using Payme receipts.

        Args:
            transaction_id: The receipt ID to check

        Returns:
            Dict containing payment status and details
        """
        receipt_data = self.receipts.check(receipt_id=transaction_id)

        # Extract receipt status
        receipt = receipt_data.get('receipt', {})
        status = receipt.get('state')

        # Map Payme status to our status
        status_mapping = {
            0: 'created',
            1: 'waiting',
            2: 'paid',
            3: 'cancelled',
            4: 'refunded'
        }

        mapped_status = status_mapping.get(status, 'unknown')

        return {
            'transaction_id': transaction_id,
            'status': mapped_status,
            'amount': receipt.get('amount') / 100,  # Convert from tiyin to som
            'paid_at': receipt.get('pay_time'),
            'created_at': receipt.get('create_time'),
            'cancelled_at': receipt.get('cancel_time'),
            'raw_response': receipt_data
        }

    @handle_exceptions
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
        receipt_data = self.receipts.cancel(
            receipt_id=transaction_id,
            reason=reason or "Cancelled by merchant"
        )

        # Extract receipt status
        receipt = receipt_data.get('receipt', {})
        status = receipt.get('state')

        return {
            'transaction_id': transaction_id,
            'status': 'cancelled' if status == 3 else 'unknown',
            'cancelled_at': receipt.get('cancel_time'),
            'raw_response': receipt_data
        }
