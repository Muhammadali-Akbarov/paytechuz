"""
Atmos payment gateway internal implementation.
This module contains the actual business logic and will be compiled to .so
"""
import base64
import logging
from typing import Dict, Any, Optional, Union

from paytechuz.core.utils import handle_exceptions

logger = logging.getLogger(__name__)


class AtmosGatewayInternal:
    """Internal implementation of Atmos gateway logic."""

    def __init__(self, consumer_key: str, consumer_secret: str, store_id: str,
                 terminal_id: Optional[str], is_test_mode: bool, client):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.store_id = store_id
        self.terminal_id = terminal_id
        self.is_test_mode = is_test_mode
        self.client = client
        self._access_token = None

    def _get_access_token(self) -> str:
        """Get access token for API authentication."""
        try:
            # Create basic auth header
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(
                credentials.encode('utf-8')).decode('utf-8')

            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {'grant_type': 'client_credentials'}

            response = self.client.post('/token', data=data, headers=headers)

            if response.get('access_token'):
                self._access_token = response['access_token']
                return self._access_token

            raise ValueError("Failed to get access token")

        except Exception as e:
            logger.error("Error getting access token: %s", e)
            raise

    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Atmos API."""
        if not self._access_token:
            self._get_access_token()

        headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = self.client.post(endpoint, json_data=data, headers=headers)
            return response
        except Exception as e:
            logger.error("API request failed: %s", e)
            raise

    @handle_exceptions
    def create_payment(
        self,
        account_id: Union[int, str],
        amount: Union[int, float, str],
        **kwargs
    ) -> Dict[str, Any]:
        """Create a payment transaction."""
        # Convert amount to tiyin (multiply by 100)
        amount_tiyin = int(float(amount) * 100)

        # Prepare request data
        create_data = {
            'amount': amount_tiyin,
            'account': str(account_id),
            'store_id': self.store_id
        }

        # Add terminal_id if provided
        if self.terminal_id:
            create_data['terminal_id'] = self.terminal_id

        # Create transaction
        response = self._make_request('/merchant/pay/create', create_data)
        transaction_id = response['transaction_id']

        # Generate payment URL
        if self.is_test_mode:
            base_url = "https://test-checkout.pays.uz/invoice/get"
        else:
            base_url = "https://checkout.pays.uz/invoice/get"

        payment_url = (f"{base_url}?storeId={self.store_id}"
                       f"&transactionId={transaction_id}")

        return {
            'transaction_id': transaction_id,
            'payment_url': payment_url,
            'amount': amount,
            'account': str(account_id),
            'status': 'created'
        }

    @handle_exceptions
    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Check payment status."""
        data = {
            'transaction_id': transaction_id,
            'store_id': self.store_id
        }

        response = self._make_request('/merchant/pay/get-status', data)

        return {
            'transaction_id': transaction_id,
            'status': response.get('status', 'unknown'),
            'details': response
        }

    @handle_exceptions
    def cancel_payment(
        self,
        transaction_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cancel payment."""
        data = {
            'transaction_id': transaction_id,
            'store_id': self.store_id
        }

        if reason:
            data['reason'] = reason

        response = self._make_request('/merchant/pay/cancel', data)

        return {
            'transaction_id': transaction_id,
            'status': 'cancelled',
            'details': response
        }
