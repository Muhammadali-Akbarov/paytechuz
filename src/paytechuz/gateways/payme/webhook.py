"""
Payme webhook handler.
"""
import base64
import binascii
import logging
from typing import Dict, Any, Optional, Callable

from paytechuz.core.base import BaseWebhookHandler
from paytechuz.core.constants import TransactionState, PaymeCancelReason
from paytechuz.core.exceptions import (
    PermissionDenied,
    MethodNotFound,
    TransactionNotFound,
    AccountNotFound,
    InternalServiceError,
    TransactionCancelled
)
from paytechuz.core.utils import handle_exceptions

logger = logging.getLogger(__name__)

class PaymeWebhookHandler(BaseWebhookHandler):
    """
    Payme webhook handler.

    This class handles webhook requests from the Payme payment system,
    including transaction creation, confirmation, and cancellation.
    """

    def __init__(
        self,
        merchant_key: str,
        find_transaction_func: Callable[[str], Dict[str, Any]],
        find_account_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        create_transaction_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        perform_transaction_func: Callable[[str], bool],
        cancel_transaction_func: Callable[[str, int], bool],
        get_statement_func: Optional[Callable[[int, int], list]] = None,
        check_perform_func: Optional[Callable[[Dict[str, Any]], bool]] = None,
        set_fiscal_data_func: Optional[
            Callable[[str, Dict[str, Any]], bool]
        ] = None
    ):
        """
        Initialize the Payme webhook handler.

        Args:
            merchant_key: Payme merchant key for authentication
            find_transaction_func: Function to find a transaction by ID
            find_account_func: Function to find an account by parameters
            create_transaction_func: Function to create a transaction
            perform_transaction_func: Function to perform a transaction
            cancel_transaction_func: Function to cancel a transaction
            get_statement_func: Function to get transaction statement
            check_perform_func: Function to check transaction can be performed
            set_fiscal_data_func: Function to set fiscal data for a transaction
        """
        self.merchant_key = merchant_key
        self.find_transaction = find_transaction_func
        self.find_account = find_account_func
        self.create_transaction = create_transaction_func
        self.perform_transaction = perform_transaction_func
        self.cancel_transaction = cancel_transaction_func
        self.get_statement = get_statement_func
        self.check_perform = check_perform_func
        self.set_fiscal_data = set_fiscal_data_func

    def _check_auth(self, auth_header: Optional[str]) -> None:
        """
        Check authentication header.

        Args:
            auth_header: Authentication header

        Raises:
            PermissionDenied: If authentication fails
        """
        if not auth_header:
            raise PermissionDenied("Missing authentication credentials")

        try:
            auth_parts = auth_header.split()
            if len(auth_parts) != 2 or auth_parts[0].lower() != 'basic':
                raise PermissionDenied("Invalid authentication format")

            auth_decoded = base64.b64decode(auth_parts[1]).decode('utf-8')
            _, password = auth_decoded.split(':')

            if password != self.merchant_key:
                raise PermissionDenied("Invalid merchant key")
        except (binascii.Error, UnicodeDecodeError, ValueError) as e:
            logger.error(f"Authentication error: {e}")
            raise PermissionDenied("Authentication error")

    @handle_exceptions
    def handle_webhook(
        self, data: Dict[str, Any], auth_header: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle webhook data from Payme.

        Args:
            data: The webhook data received from Payme
            auth_header: Authentication header

        Returns:
            Dict containing the response to be sent back to Payme

        Raises:
            PermissionDenied: If authentication fails
            MethodNotFound: If the requested method is not supported
        """
        # Check authentication
        self._check_auth(auth_header)

        # Extract method and params
        try:
            method = data.get('method')
            params = data.get('params', {})
            request_id = data.get('id', 0)
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid webhook data: {e}")
            raise InternalServiceError("Invalid webhook data")

        # Map methods to handler functions
        method_handlers = {
            'CheckPerformTransaction': self._handle_check_perform,
            'CreateTransaction': self._handle_create_transaction,
            'PerformTransaction': self._handle_perform_transaction,
            'CheckTransaction': self._handle_check_transaction,
            'CancelTransaction': self._handle_cancel_transaction,
            'GetStatement': self._handle_get_statement,
            'SetFiscalData': self._handle_set_fiscal_data,
        }

        # Call the appropriate handler
        if method in method_handlers:
            result = method_handlers[method](params)
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }

        logger.warning(f"Method not found: {method}")
        raise MethodNotFound(f"Method not supported: {method}")

    def _handle_check_perform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CheckPerformTransaction method.

        Args:
            params: Method parameters

        Returns:
            Dict containing the response
        """
        if not self.check_perform:
            # Default implementation if no custom function is provided
            account = self.find_account(params.get('account', {}))
            if not account:
                raise AccountNotFound("Account not found")

            return {'allow': True}

        # Call custom function
        result = self.check_perform(params)
        return {'allow': result}

    def _handle_create_transaction(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle CreateTransaction method.

        Args:
            params: Method parameters

        Returns:
            Dict containing the response
        """
        transaction_id = params.get('id')

        # Check if transaction already exists
        try:
            existing_transaction = self.find_transaction(transaction_id)

            # If transaction exists, return its details
            return {
                'transaction': existing_transaction['id'],
                'state': existing_transaction['state'],
                'create_time': existing_transaction['create_time'],
            }
        except TransactionNotFound:
            # Transaction doesn't exist, create a new one
            pass

        # Find account
        account = self.find_account(params.get('account', {}))
        if not account:
            raise AccountNotFound("Account not found")

        # Create transaction
        transaction = self.create_transaction({
            'id': transaction_id,
            'account': account,
            'amount': params.get('amount'),
            'time': params.get('time'),
        })

        return {
            'transaction': transaction['id'],
            'state': transaction['state'],
            'create_time': transaction['create_time'],
        }

    def _handle_perform_transaction(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle PerformTransaction method.

        Args:
            params: Method parameters

        Returns:
            Dict containing the response
        """
        transaction_id = params.get('id')

        # Find transaction
        transaction = self.find_transaction(transaction_id)

        # Perform transaction
        self.perform_transaction(transaction_id)

        return {
            'transaction': transaction['id'],
            'state': transaction['state'],
            'perform_time': transaction.get('perform_time', 0),
        }

    def _handle_check_transaction(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle CheckTransaction method.

        Args:
            params: Method parameters

        Returns:
            Dict containing the response
        """
        transaction_id = params.get('id')

        # Find transaction
        transaction = self.find_transaction(transaction_id)

        return {
            'transaction': transaction['id'],
            'state': transaction['state'],
            'create_time': transaction['create_time'],
            'perform_time': transaction.get('perform_time', 0),
            'cancel_time': transaction.get('cancel_time', 0),
            'reason': transaction.get('reason'),
        }

    def _cancel_response(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper method to generate cancel transaction response.

        Args:
            transaction: Transaction data

        Returns:
            Dict containing the response
        """
        return {
            'transaction': transaction['id'],
            'state': transaction['state'],
            'cancel_time': transaction.get('cancel_time', 0),
        }

    def _handle_cancel_transaction(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle CancelTransaction method.

        Args:
            params: Method parameters

        Returns:
            Dict containing the response
        """
        transaction_id = params.get('id')
        reason = params.get(
            'reason', PaymeCancelReason.REASON_MERCHANT_DECISION
        )

        # Find transaction
        transaction = self.find_transaction(transaction_id)

        # Check if transaction is already cancelled
        canceled_states = [
            TransactionState.CANCELED.value,
            TransactionState.CANCELED_DURING_INIT.value
        ]
        if transaction.get('state') in canceled_states:
            # If transaction is already cancelled, return the existing data
            return self._cancel_response(transaction)

        # Check if transaction can be cancelled based on its current state
        if transaction.get('state') == TransactionState.SUCCESSFULLY.value:
            # Transaction was successfully performed, can be cancelled
            pass
        elif transaction.get('state') == TransactionState.INITIATING.value:
            # Transaction is in initiating state, can be cancelled
            pass
        else:
            # If transaction is in another state, it cannot be cancelled
            raise TransactionCancelled(
                f"Transaction {transaction_id} cannot be cancelled"
            )

        # Cancel transaction
        self.cancel_transaction(transaction_id, reason)

        # Get updated transaction
        updated_transaction = self.find_transaction(transaction_id)

        # Return cancel response
        return self._cancel_response(updated_transaction)

    def _handle_get_statement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle GetStatement method.

        Args:
            params: Method parameters

        Returns:
            Dict containing the response
        """
        if not self.get_statement:
            raise MethodNotFound("GetStatement method not implemented")

        from_date = params.get('from')
        to_date = params.get('to')

        # Get statement
        transactions = self.get_statement(from_date, to_date)

        return {'transactions': transactions}

    def _handle_set_fiscal_data(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle SetFiscalData method.

        Args:
            params: Method parameters

        Returns:
            Dict containing the response
        """
        if not self.set_fiscal_data:
            raise MethodNotFound("SetFiscalData method not implemented")

        transaction_id = params.get('id')
        fiscal_data = params.get('fiscal_data', {})

        # Set fiscal data
        success = self.set_fiscal_data(transaction_id, fiscal_data)

        return {'success': success}
