"""
Flask routes for PayTechUZ.
"""
import base64
import hashlib
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, Callable

from flask import Blueprint, request, jsonify, current_app

from .models import PaymentTransaction, db

logger = logging.getLogger(__name__)

blueprint = Blueprint('paytechuz', __name__)


class PaymeWebhookHandler:
    """
    Base Payme webhook handler for Flask.
    
    This class handles webhook requests from the Payme payment system.
    You can extend this class and override the event methods to customize
    the behavior.
    
    Example:
    ```python
    from paytechuz.integrations.flask.routes import PaymeWebhookHandler
    
    class CustomPaymeWebhookHandler(PaymeWebhookHandler):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")
            
            # Update your order status
            order = Order.query.get(transaction.account_id)
            order.status = 'paid'
            db.session.commit()
    ```
    """
    
    def __init__(
        self,
        payme_id: str,
        payme_key: str,
        account_model: Any,
        account_field: str = 'id',
        amount_field: str = 'amount',
        one_time_payment: bool = True
    ):
        """
        Initialize the Payme webhook handler.
        
        Args:
            payme_id: Payme merchant ID
            payme_key: Payme merchant key
            account_model: Account model class
            account_field: Account field name
            amount_field: Amount field name
            one_time_payment: Whether to validate amount
        """
        self.payme_id = payme_id
        self.payme_key = payme_key
        self.account_model = account_model
        self.account_field = account_field
        self.amount_field = amount_field
        self.one_time_payment = one_time_payment
    
    def handle_webhook(self) -> Dict[str, Any]:
        """
        Handle webhook request from Payme.
        
        Returns:
            Response data
        """
        try:
            # Check authorization
            auth_header = request.headers.get('Authorization')
            self._check_auth(auth_header)
            
            # Parse request data
            data = request.get_json()
            method = data.get('method')
            params = data.get('params', {})
            request_id = data.get('id', 0)
            
            # Process the request based on the method
            if method == 'CheckPerformTransaction':
                result = self._check_perform_transaction(params)
            elif method == 'CreateTransaction':
                result = self._create_transaction(params)
            elif method == 'PerformTransaction':
                result = self._perform_transaction(params)
            elif method == 'CheckTransaction':
                result = self._check_transaction(params)
            elif method == 'CancelTransaction':
                result = self._cancel_transaction(params)
            elif method == 'GetStatement':
                result = self._get_statement(params)
            else:
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32601,
                        'message': f"Method not supported: {method}"
                    }
                })
            
            # Return the result
            return jsonify({
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            })
        
        except Exception as e:
            logger.exception(f"Unexpected error in Payme webhook: {e}")
            return jsonify({
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 0,
                'error': {
                    'code': -32400,
                    'message': 'Internal error'
                }
            })
    
    def _check_auth(self, auth_header: Optional[str]) -> None:
        """
        Check authorization header.
        """
        if not auth_header:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -32504,
                    'message': "Missing authentication credentials"
                }
            })
        
        try:
            auth_parts = auth_header.split()
            if len(auth_parts) != 2 or auth_parts[0].lower() != 'basic':
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': 0,
                    'error': {
                        'code': -32504,
                        'message': "Invalid authentication format"
                    }
                })
            
            auth_decoded = base64.b64decode(auth_parts[1]).decode('utf-8')
            username, password = auth_decoded.split(':')
            
            if password != self.payme_key:
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': 0,
                    'error': {
                        'code': -32504,
                        'message': "Invalid merchant key"
                    }
                })
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -32504,
                    'message': "Authentication error"
                }
            })
    
    def _find_account(self, params: Dict[str, Any]) -> Any:
        """
        Find account by parameters.
        """
        account_value = params.get('account', {}).get(self.account_field)
        if not account_value:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -31050,
                    'message': "Account not found in parameters"
                }
            })
        
        # Handle special case for 'order_id' field
        lookup_field = 'id' if self.account_field == 'order_id' else self.account_field
        
        # Try to convert account_value to int if it's a string and lookup_field is 'id'
        if lookup_field == 'id' and isinstance(account_value, str) and account_value.isdigit():
            account_value = int(account_value)
        
        account = self.account_model.query.filter_by(**{lookup_field: account_value}).first()
        if not account:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -31050,
                    'message': f"Account with {self.account_field}={account_value} not found"
                }
            })
        
        return account
    
    def _validate_amount(self, account: Any, amount: int) -> bool:
        """
        Validate payment amount.
        """
        # If one_time_payment is disabled, we still validate the amount
        # but we don't require it to match exactly
        
        expected_amount = Decimal(getattr(account, self.amount_field)) * 100
        received_amount = Decimal(amount)
        
        # If one_time_payment is enabled, amount must match exactly
        if self.one_time_payment and expected_amount != received_amount:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -31001,
                    'message': f"Invalid amount. Expected: {expected_amount}, received: {received_amount}"
                }
            })
        
        # If one_time_payment is disabled, amount must be positive
        if not self.one_time_payment and received_amount <= 0:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -31001,
                    'message': f"Invalid amount. Amount must be positive, received: {received_amount}"
                }
            })
        
        return True
    
    def _check_perform_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CheckPerformTransaction method.
        """
        account = self._find_account(params)
        self._validate_amount(account, params.get('amount'))
        
        # Call the event method
        self.before_check_perform_transaction(params, account)
        
        return {'allow': True}
    
    def _create_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CreateTransaction method.
        """
        transaction_id = params.get('id')
        account = self._find_account(params)
        amount = params.get('amount')
        
        self._validate_amount(account, amount)
        
        # Check if there's already a transaction for this account with a different transaction_id
        # Only check if one_time_payment is enabled
        if self.one_time_payment:
            # Check for existing transactions in non-final states
            existing_transactions = PaymentTransaction.query.filter_by(
                gateway=PaymentTransaction.PAYME,
                account_id=account.id
            ).filter(
                PaymentTransaction.transaction_id != transaction_id
            ).all()
            
            # Filter out transactions in final states (SUCCESSFULLY, CANCELLED)
            non_final_transactions = [
                t for t in existing_transactions 
                if t.state not in [PaymentTransaction.SUCCESSFULLY, PaymentTransaction.CANCELLED]
            ]
            
            if non_final_transactions:
                # If there's already a transaction for this account with a different transaction_id in a non-final state, raise an error
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': 0,
                    'error': {
                        'code': -31050,
                        'message': f"Account with {self.account_field}={account.id} already has a pending transaction"
                    }
                })
        
        # Check for existing transaction with the same transaction_id
        transaction = PaymentTransaction.query.filter_by(
            gateway=PaymentTransaction.PAYME,
            transaction_id=transaction_id
        ).first()
        
        if transaction:
            # Call the event method
            self.transaction_already_exists(params, transaction)
            
            return {
                'transaction': transaction.transaction_id,
                'state': transaction.state,
                'create_time': int(transaction.created_at.timestamp() * 1000),
            }
        
        # Create new transaction
        transaction = PaymentTransaction(
            gateway=PaymentTransaction.PAYME,
            transaction_id=transaction_id,
            account_id=account.id,
            amount=Decimal(amount) / 100,  # Convert from tiyin to som
            state=PaymentTransaction.INITIATING,
            extra_data={
                'account_field': self.account_field,
                'account_value': params.get('account', {}).get(self.account_field),
                'create_time': params.get('time'),
                'raw_params': params
            }
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Call the event method
        self.transaction_created(params, transaction, account)
        
        return {
            'transaction': transaction.transaction_id,
            'state': transaction.state,
            'create_time': int(transaction.created_at.timestamp() * 1000),
        }
    
    def _perform_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle PerformTransaction method.
        """
        transaction_id = params.get('id')
        
        transaction = PaymentTransaction.query.filter_by(
            gateway=PaymentTransaction.PAYME,
            transaction_id=transaction_id
        ).first()
        
        if not transaction:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -31003,
                    'message': f"Transaction {transaction_id} not found"
                }
            })
        
        # Mark transaction as paid
        transaction.mark_as_paid()
        db.session.commit()
        
        # Call the event method
        self.successfully_payment(params, transaction)
        
        return {
            'transaction': transaction.transaction_id,
            'state': transaction.state,
            'perform_time': int(transaction.performed_at.timestamp() * 1000) if transaction.performed_at else 0,
        }
    
    def _check_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CheckTransaction method.
        """
        transaction_id = params.get('id')
        
        transaction = PaymentTransaction.query.filter_by(
            gateway=PaymentTransaction.PAYME,
            transaction_id=transaction_id
        ).first()
        
        if not transaction:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -31003,
                    'message': f"Transaction {transaction_id} not found"
                }
            })
        
        # Call the event method
        self.check_transaction(params, transaction)
        
        return {
            'transaction': transaction.transaction_id,
            'state': transaction.state,
            'create_time': int(transaction.created_at.timestamp() * 1000),
            'perform_time': int(transaction.performed_at.timestamp() * 1000) if transaction.performed_at else 0,
            'cancel_time': int(transaction.cancelled_at.timestamp() * 1000) if transaction.cancelled_at else 0,
            'reason': transaction.extra_data.get('cancel_reason') if transaction.extra_data else None,
        }
    
    def _cancel_response(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """
        Helper method to generate cancel transaction response.
        
        Args:
            transaction: Transaction object
            
        Returns:
            Dict containing the response
        """
        return {
            'transaction': transaction.transaction_id,
            'state': transaction.state,
            'cancel_time': int(transaction.cancelled_at.timestamp() * 1000) if transaction.cancelled_at else 0,
        }
    
    def _cancel_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CancelTransaction method.
        """
        transaction_id = params.get('id')
        reason = params.get('reason')
        
        transaction = PaymentTransaction.query.filter_by(
            gateway=PaymentTransaction.PAYME,
            transaction_id=transaction_id
        ).first()
        
        if not transaction:
            return jsonify({
                'jsonrpc': '2.0',
                'id': 0,
                'error': {
                    'code': -31003,
                    'message': f"Transaction {transaction_id} not found"
                }
            })
        
        # Check if transaction is already cancelled
        if transaction.state == PaymentTransaction.CANCELLED:
            # If transaction is already cancelled, return the existing data
            return self._cancel_response(transaction)
        
        # Mark transaction as cancelled
        transaction.mark_as_cancelled(reason=reason)
        db.session.commit()
        
        # Call the event method
        self.cancelled_payment(params, transaction)
        
        # Return cancel response
        return self._cancel_response(transaction)
    
    def _get_statement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle GetStatement method.
        """
        from_date = params.get('from')
        to_date = params.get('to')
        
        # Convert milliseconds to datetime objects
        if from_date:
            from_datetime = datetime.fromtimestamp(from_date / 1000)
        else:
            from_datetime = datetime.fromtimestamp(0)  # Unix epoch start
        
        if to_date:
            to_datetime = datetime.fromtimestamp(to_date / 1000)
        else:
            to_datetime = datetime.now()  # Current time
        
        # Get transactions in the date range
        transactions = PaymentTransaction.query.filter(
            PaymentTransaction.gateway == PaymentTransaction.PAYME,
            PaymentTransaction.created_at >= from_datetime,
            PaymentTransaction.created_at <= to_datetime
        ).all()
        
        # Format transactions for response
        result = []
        for transaction in transactions:
            result.append({
                'id': transaction.transaction_id,
                'time': int(transaction.created_at.timestamp() * 1000),
                'amount': int(transaction.amount * 100),  # Convert to tiyin
                'account': {
                    self.account_field: transaction.account_id
                },
                'state': transaction.state,
                'create_time': int(transaction.created_at.timestamp() * 1000),
                'perform_time': int(transaction.performed_at.timestamp() * 1000) if transaction.performed_at else 0,
                'cancel_time': int(transaction.cancelled_at.timestamp() * 1000) if transaction.cancelled_at else 0,
                'reason': transaction.extra_data.get('cancel_reason') if transaction.extra_data else None,
            })
        
        # Call the event method
        self.get_statement(params, result)
        
        return {'transactions': result}
    
    # Event methods that can be overridden by subclasses
    
    def before_check_perform_transaction(self, params: Dict[str, Any], account: Any) -> None:
        """
        Called before checking if a transaction can be performed.
        
        Args:
            params: Request parameters
            account: Account object
        """
        pass
    
    def transaction_already_exists(self, params: Dict[str, Any], transaction: PaymentTransaction) -> None:
        """
        Called when a transaction already exists.
        
        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass
    
    def transaction_created(self, params: Dict[str, Any], transaction: PaymentTransaction, account: Any) -> None:
        """
        Called when a transaction is created.
        
        Args:
            params: Request parameters
            transaction: Transaction object
            account: Account object
        """
        pass
    
    def successfully_payment(self, params: Dict[str, Any], transaction: PaymentTransaction) -> None:
        """
        Called when a payment is successful.
        
        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass
    
    def check_transaction(self, params: Dict[str, Any], transaction: PaymentTransaction) -> None:
        """
        Called when checking a transaction.
        
        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass
    
    def cancelled_payment(self, params: Dict[str, Any], transaction: PaymentTransaction) -> None:
        """
        Called when a payment is cancelled.
        
        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass
    
    def get_statement(self, params: Dict[str, Any], transactions: list) -> None:
        """
        Called when getting a statement.
        
        Args:
            params: Request parameters
            transactions: List of transactions
        """
        pass


class ClickWebhookHandler:
    """
    Base Click webhook handler for Flask.
    
    This class handles webhook requests from the Click payment system.
    You can extend this class and override the event methods to customize
    the behavior.
    
    Example:
    ```python
    from paytechuz.integrations.flask.routes import ClickWebhookHandler
    
    class CustomClickWebhookHandler(ClickWebhookHandler):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")
            
            # Update your order status
            order = Order.query.get(transaction.account_id)
            order.status = 'paid'
            db.session.commit()
    ```
    """
    
    def __init__(
        self,
        service_id: str,
        secret_key: str,
        account_model: Any,
        commission_percent: float = 0.0
    ):
        """
        Initialize the Click webhook handler.
        
        Args:
            service_id: Click service ID
            secret_key: Click secret key
            account_model: Account model class
            commission_percent: Commission percentage
        """
        self.service_id = service_id
        self.secret_key = secret_key
        self.account_model = account_model
        self.commission_percent = commission_percent
    
    def handle_webhook(self) -> Dict[str, Any]:
        """
        Handle webhook request from Click.
        
        Returns:
            Response data
        """
        try:
            # Get parameters from request
            params = request.form.to_dict()
            
            # Check authorization
            self._check_auth(params)
            
            # Extract parameters
            click_trans_id = params.get('click_trans_id')
            merchant_trans_id = params.get('merchant_trans_id')
            amount = float(params.get('amount', 0))
            action = int(params.get('action', -1))
            error = int(params.get('error', 0))
            
            # Find account
            try:
                account = self._find_account(merchant_trans_id)
            except Exception as e:
                logger.error(f"Account not found: {merchant_trans_id}")
                return jsonify({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'error': -5,
                    'error_note': "User not found"
                })
            
            # Validate amount
            try:
                self._validate_amount(amount, float(getattr(account, 'amount', 0)))
            except Exception as e:
                logger.error(f"Invalid amount: {e}")
                return jsonify({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'error': -2,
                    'error_note': str(e)
                })
            
            # Check if transaction already exists
            transaction = PaymentTransaction.query.filter_by(
                gateway=PaymentTransaction.CLICK,
                transaction_id=click_trans_id
            ).first()
            
            if transaction:
                # If transaction is already completed, return success
                if transaction.state == PaymentTransaction.SUCCESSFULLY:
                    # Call the event method
                    self.transaction_already_exists(params, transaction)
                    
                    return jsonify({
                        'click_trans_id': click_trans_id,
                        'merchant_trans_id': merchant_trans_id,
                        'merchant_prepare_id': transaction.id,
                        'error': 0,
                        'error_note': "Success"
                    })
                
                # If transaction is cancelled, return error
                if transaction.state == PaymentTransaction.CANCELLED:
                    return jsonify({
                        'click_trans_id': click_trans_id,
                        'merchant_trans_id': merchant_trans_id,
                        'merchant_prepare_id': transaction.id,
                        'error': -9,
                        'error_note': "Transaction cancelled"
                    })
            
            # Handle different actions
            if action == 0:  # Prepare
                # Create transaction
                transaction = PaymentTransaction(
                    gateway=PaymentTransaction.CLICK,
                    transaction_id=click_trans_id,
                    account_id=merchant_trans_id,
                    amount=amount,
                    state=PaymentTransaction.INITIATING,
                    extra_data={
                        'raw_params': params
                    }
                )
                
                db.session.add(transaction)
                db.session.commit()
                
                # Call the event method
                self.transaction_created(params, transaction, account)
                
                return jsonify({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'merchant_prepare_id': transaction.id,
                    'error': 0,
                    'error_note': "Success"
                })
            
            elif action == 1:  # Complete
                # Check if error is negative (payment failed)
                is_successful = error >= 0
                
                if not transaction:
                    # Create transaction if it doesn't exist
                    transaction = PaymentTransaction(
                        gateway=PaymentTransaction.CLICK,
                        transaction_id=click_trans_id,
                        account_id=merchant_trans_id,
                        amount=amount,
                        state=PaymentTransaction.INITIATING,
                        extra_data={
                            'raw_params': params
                        }
                    )
                    
                    db.session.add(transaction)
                    db.session.commit()
                
                if is_successful:
                    # Mark transaction as paid
                    transaction.mark_as_paid()
                    db.session.commit()
                    
                    # Call the event method
                    self.successfully_payment(params, transaction)
                else:
                    # Mark transaction as cancelled
                    transaction.mark_as_cancelled(reason=f"Error code: {error}")
                    db.session.commit()
                    
                    # Call the event method
                    self.cancelled_payment(params, transaction)
                
                return jsonify({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'merchant_prepare_id': transaction.id,
                    'error': 0,
                    'error_note': "Success"
                })
            
            else:
                logger.error(f"Unsupported action: {action}")
                return jsonify({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'error': -3,
                    'error_note': "Action not found"
                })
        
        except Exception as e:
            logger.exception(f"Unexpected error in Click webhook: {e}")
            return jsonify({
                'error': -7,
                'error_note': "Internal error"
            })
    
    def _check_auth(self, params: Dict[str, Any]) -> None:
        """
        Check authentication using signature.
        """
        if str(params.get('service_id')) != self.service_id:
            return jsonify({
                'error': -1,
                'error_note': "Invalid service ID"
            })
        
        # Check signature if secret key is provided
        if self.secret_key:
            sign_string = params.get('sign_string')
            sign_time = params.get('sign_time')
            
            if not sign_string or not sign_time:
                return jsonify({
                    'error': -1,
                    'error_note': "Missing signature parameters"
                })
            
            # Create string to sign
            to_sign = f"{params.get('click_trans_id')}{params.get('service_id')}"
            to_sign += f"{self.secret_key}{params.get('merchant_trans_id')}"
            to_sign += f"{params.get('amount')}{params.get('action')}"
            to_sign += f"{sign_time}"
            
            # Generate signature
            signature = hashlib.md5(to_sign.encode('utf-8')).hexdigest()
            
            if signature != sign_string:
                return jsonify({
                    'error': -1,
                    'error_note': "Invalid signature"
                })
    
    def _find_account(self, merchant_trans_id: str) -> Any:
        """
        Find account by merchant_trans_id.
        """
        # Try to convert merchant_trans_id to int if it's a string and a digit
        if isinstance(merchant_trans_id, str) and merchant_trans_id.isdigit():
            merchant_trans_id = int(merchant_trans_id)
        
        account = self.account_model.query.get(merchant_trans_id)
        if not account:
            raise Exception(f"Account with id={merchant_trans_id} not found")
        
        return account
    
    def _validate_amount(self, received_amount: float, expected_amount: float) -> None:
        """
        Validate payment amount.
        """
        # Add commission if needed
        if self.commission_percent > 0:
            expected_amount = expected_amount * (1 + self.commission_percent / 100)
            expected_amount = round(expected_amount, 2)
        
        # Allow small difference due to floating point precision
        if abs(received_amount - expected_amount) > 0.01:
            raise Exception(f"Incorrect amount. Expected: {expected_amount}, received: {received_amount}")
    
    # Event methods that can be overridden by subclasses
    
    def transaction_already_exists(self, params: Dict[str, Any], transaction: PaymentTransaction) -> None:
        """
        Called when a transaction already exists.
        
        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass
    
    def transaction_created(self, params: Dict[str, Any], transaction: PaymentTransaction, account: Any) -> None:
        """
        Called when a transaction is created.
        
        Args:
            params: Request parameters
            transaction: Transaction object
            account: Account object
        """
        pass
    
    def successfully_payment(self, params: Dict[str, Any], transaction: PaymentTransaction) -> None:
        """
        Called when a payment is successful.
        
        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass
    
    def cancelled_payment(self, params: Dict[str, Any], transaction: PaymentTransaction) -> None:
        """
        Called when a payment is cancelled.
        
        Args:
            params: Request parameters
            transaction: Transaction object
        """
        pass


# Create Flask routes

@blueprint.route('/payme/webhook', methods=['POST'])
def payme_webhook():
    """
    Handle Payme webhook requests.
    
    Returns:
        Response data
    """
    handler = current_app.config.get('PAYME_WEBHOOK_HANDLER')
    if not handler:
        return jsonify({
            'jsonrpc': '2.0',
            'id': 0,
            'error': {
                'code': -32500,
                'message': "Payme webhook handler not configured"
            }
        })
    
    return handler.handle_webhook()


@blueprint.route('/click/webhook', methods=['POST'])
def click_webhook():
    """
    Handle Click webhook requests.
    
    Returns:
        Response data
    """
    handler = current_app.config.get('CLICK_WEBHOOK_HANDLER')
    if not handler:
        return jsonify({
            'error': -7,
            'error_note': "Click webhook handler not configured"
        })
    
    return handler.handle_webhook()
