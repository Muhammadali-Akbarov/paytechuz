"""
Payme payment gateway internal implementation.
This module contains the actual business logic and will be compiled to .so
"""
import base64
import logging
from typing import Dict, Any, Optional, Union

from paytechuz.core.utils import handle_exceptions

logger = logging.getLogger(__name__)


class PaymeGatewayInternal:
    """Internal implementation of Payme gateway logic."""

    def __init__(self, payme_id: str, payme_key: Optional[str], fallback_id: Optional[str],
                 is_test_mode: bool, http_client, cards, receipts):
        self.payme_id = payme_id
        self.payme_key = payme_key
        self.fallback_id = fallback_id
        self.is_test_mode = is_test_mode
        self.http_client = http_client
        self.cards = cards
        self.receipts = receipts

    def generate_pay_link(
        self,
        id: Union[int, str],
        amount: Union[int, float, str],
        return_url: str,
        account_field_name: str = "order_id"
    ) -> str:
        """Generate a payment link for a specific order."""
        # Convert amount to tiyin (1 som = 100 tiyin)
        amount_tiyin = int(float(amount) * 100)

        # Build parameters
        params = (
            f'm={self.payme_id};'
            f'ac.{account_field_name}={id};'
            f'a={amount_tiyin};'
            f'c={return_url}'
        )
        encoded_params = base64.b64encode(params.encode("utf-8")).decode("utf-8")

        # Return URL based on environment
        base_url = "https://test.paycom.uz" if self.is_test_mode else "https://checkout.paycom.uz"
        return f"{base_url}/{encoded_params}"

    @handle_exceptions
    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Check payment status using Payme receipts."""
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
        """Cancel payment using Payme receipts."""
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
