"""
Click webhook handler.
"""
import hashlib
import logging
from typing import Dict, Any, Callable

from paytechuz.core.base import BaseWebhookHandler
from paytechuz.core.constants import ClickActions
from paytechuz.core.exceptions import (
    PermissionDenied,
    InvalidAmount,
    TransactionNotFound,
    UnsupportedMethod,
    AccountNotFound
)
from paytechuz.core.utils import handle_exceptions

logger = logging.getLogger(__name__)

class ClickWebhookHandler(BaseWebhookHandler):
    """
    Click webhook handler.

    This class handles webhook requests from the Click payment system,
    including transaction preparation and completion.
    """

    def __init__(
        self,
        service_id: str,
        secret_key: str,
        find_transaction_func: Callable[[str], Dict[str, Any]],
        find_account_func: Callable[[str], Dict[str, Any]],
        create_transaction_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        complete_transaction_func: Callable[[str, bool], Dict[str, Any]],
        commission_percent: float = 0.0
    ):
        """
        Initialize the Click webhook handler.

        Args:
            service_id: Click service ID
            secret_key: Secret key for authentication
            find_transaction_func: Function to find a transaction by ID
            find_account_func: Function to find an account by ID
            create_transaction_func: Function to create a transaction
            complete_transaction_func: Function to complete a transaction
            commission_percent: Commission percentage
        """
        self.service_id = service_id
        self.secret_key = secret_key
        self.find_transaction = find_transaction_func
        self.find_account = find_account_func
        self.create_transaction = create_transaction_func
        self.complete_transaction = complete_transaction_func
        self.commission_percent = commission_percent

    def _check_auth(self, params: Dict[str, Any]) -> None:
        """
        Check authentication using signature.

        Args:
            params: Request parameters

        Raises:
            PermissionDenied: If authentication fails
        """
        if str(params.get('service_id')) != self.service_id:
            raise PermissionDenied("Invalid service ID")

        # Check signature if secret key is provided
        if self.secret_key:
            sign_string = params.get('sign_string')
            sign_time = params.get('sign_time')

            if not sign_string or not sign_time:
                raise PermissionDenied("Missing signature parameters")

            # Create string to sign
            to_sign = f"{params.get('click_trans_id')}{params.get('service_id')}"
            to_sign += f"{self.secret_key}{params.get('merchant_trans_id')}"
            to_sign += f"{params.get('amount')}{params.get('action')}"
            to_sign += f"{sign_time}"

            # Generate signature
            signature = hashlib.md5(to_sign.encode('utf-8')).hexdigest()

            if signature != sign_string:
                raise PermissionDenied("Invalid signature")

    def _validate_amount(
        self,
        received_amount: float,
        expected_amount: float
    ) -> None:
        """
        Validate payment amount.

        Args:
            received_amount: Amount received from Click
            expected_amount: Expected amount

        Raises:
            InvalidAmount: If amounts don't match
        """
        # Add commission if needed
        if self.commission_percent > 0:
            expected_amount = expected_amount * (1 + self.commission_percent / 100)
            expected_amount = round(expected_amount, 2)

        # Allow small difference due to floating point precision
        if abs(received_amount - expected_amount) > 0.01:
            raise InvalidAmount(f"Incorrect amount. Expected: {expected_amount}, received: {received_amount}")

    @handle_exceptions
    def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook data from Click.

        Args:
            data: The webhook data received from Click

        Returns:
            Dict containing the response to be sent back to Click

        Raises:
            PermissionDenied: If authentication fails
            UnsupportedMethod: If the requested action is not supported
        """
        # Check authentication
        self._check_auth(data)

        # Extract parameters
        click_trans_id = data.get('click_trans_id')
        merchant_trans_id = data.get('merchant_trans_id')
        amount = float(data.get('amount', 0))
        action = int(data.get('action', -1))
        error = int(data.get('error', 0))

        # Find account
        try:
            account = self.find_account(merchant_trans_id)
        except AccountNotFound:
            logger.error(f"Account not found: {merchant_trans_id}")
            return {
                'click_trans_id': click_trans_id,
                'merchant_trans_id': merchant_trans_id,
                'error': -5,
                'error_note': "User not found"
            }

        # Validate amount
        try:
            self._validate_amount(amount, float(account.get('amount', 0)))
        except InvalidAmount as e:
            logger.error(f"Invalid amount: {e}")
            return {
                'click_trans_id': click_trans_id,
                'merchant_trans_id': merchant_trans_id,
                'error': -2,
                'error_note': str(e)
            }

        # Check if transaction already exists
        try:
            transaction = self.find_transaction(click_trans_id)

            # If transaction is already completed, return success
            if transaction.get('state') == 2:  # SUCCESSFULLY
                return {
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'merchant_prepare_id': transaction.get('id'),
                    'error': 0,
                    'error_note': "Success"
                }

            # If transaction is cancelled, return error
            if transaction.get('state') == -2:  # CANCELLED
                return {
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'merchant_prepare_id': transaction.get('id'),
                    'error': -9,
                    'error_note': "Transaction cancelled"
                }
        except TransactionNotFound:
            # Transaction doesn't exist, continue with the flow
            pass

        # Handle different actions
        if action == ClickActions.PREPARE:
            # Create transaction
            transaction = self.create_transaction({
                'click_trans_id': click_trans_id,
                'merchant_trans_id': merchant_trans_id,
                'amount': amount,
                'account': account
            })

            return {
                'click_trans_id': click_trans_id,
                'merchant_trans_id': merchant_trans_id,
                'merchant_prepare_id': transaction.get('id'),
                'error': 0,
                'error_note': "Success"
            }

        elif action == ClickActions.COMPLETE:
            # Check if error is negative (payment failed)
            is_successful = error >= 0

            # Complete transaction
            transaction = self.complete_transaction(click_trans_id, is_successful)

            return {
                'click_trans_id': click_trans_id,
                'merchant_trans_id': merchant_trans_id,
                'merchant_prepare_id': transaction.get('id'),
                'error': 0,
                'error_note': "Success"
            }

        else:
            logger.error(f"Unsupported action: {action}")
            raise UnsupportedMethod(f"Unsupported action: {action}")
