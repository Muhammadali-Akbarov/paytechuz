"""
Atmos webhook handler.
"""
import hashlib
import logging
from typing import Dict, Any

from paytechuz.core.base import BaseWebhookHandler

logger = logging.getLogger(__name__)


class AtmosWebhookHandler(BaseWebhookHandler):
    """
    Atmos webhook handler for processing payment notifications.
    """

    def __init__(self, api_key: str):
        """
        Initialize the webhook handler.

        Args:
            api_key: API key for signature verification
        """
        self.api_key = api_key

    def verify_signature(self, webhook_data: Dict[str, Any],
                         received_signature: str) -> bool:
        """
        Verify webhook signature from Atmos.

        Args:
            webhook_data: The webhook data received
            received_signature: The signature received from Atmos

        Returns:
            bool: True if signature is valid, False otherwise
        """
        # Extract data from webhook
        store_id = str(webhook_data.get('store_id', ''))
        transaction_id = str(webhook_data.get('transaction_id', ''))
        invoice = str(webhook_data.get('invoice', ''))
        amount = str(webhook_data.get('amount', ''))

        # Create signature string:
        # store_id+transaction_id+invoice+amount+api_key
        signature_string = (f"{store_id}{transaction_id}{invoice}"
                            f"{amount}{self.api_key}")

        # Generate MD5 hash
        calculated_signature = hashlib.md5(
            signature_string.encode('utf-8')).hexdigest()

        # Compare signatures
        return calculated_signature == received_signature

    def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook data from Atmos.

        Args:
            data: The webhook data received from Atmos

        Returns:
            Dict containing the response to be sent back to Atmos
        """
        try:
            # Extract signature
            received_signature = data.get('sign', '')

            # Verify signature
            if not self.verify_signature(data, received_signature):
                logger.error("Invalid webhook signature")
                return {
                    'status': 0,
                    'message': 'Invalid signature'
                }

            # Extract webhook data
            transaction_id = data.get('transaction_id')
            amount = data.get('amount')
            invoice = data.get('invoice')

            logger.info("Webhook received for transaction %s, "
                        "invoice %s, amount %s",
                        transaction_id, invoice, amount)

            # Return success response
            return {
                'status': 1,
                'message': 'Успешно'
            }

        except ValueError as e:
            logger.error("Webhook processing error: %s", e)
            return {
                'status': 0,
                'message': f'Error: {str(e)}'
            }
