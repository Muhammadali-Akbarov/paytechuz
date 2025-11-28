"""
Django webhook handlers for PayTechUZ.
"""
import base64
import hashlib
import json
import logging
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django.views import View

from paytechuz.core.exceptions import (
    PermissionDenied,
    InvalidAmount,
    TransactionNotFound,
    AccountNotFound,
    MethodNotFound,
    UnsupportedMethod
)
from .models import PaymentTransaction

logger = logging.getLogger(__name__)


class PaymeWebhook(View):
    """
    Base Payme webhook handler for Django.

    This class handles webhook requests from the Payme payment system.
    You can extend this class and override the event methods to customize
    the behavior.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        paytechuz_settings = getattr(settings, 'PAYTECHUZ', {})
        payme_settings = paytechuz_settings.get('PAYME', {})

        self.payme_id = payme_settings.get('PAYME_ID') or getattr(settings, 'PAYME_ID', '')
        self.payme_key = payme_settings.get('PAYME_KEY') or getattr(settings, 'PAYME_KEY', '')

        account_model_path = (
            payme_settings.get('ACCOUNT_MODEL') or 
            getattr(settings, 'PAYME_ACCOUNT_MODEL', 'django.contrib.auth.models.User')
        )
        try:
            self.account_model = import_string(account_model_path)
        except ImportError:
            logger.error(
                "Could not import %s. Check PAYTECHUZ.PAYME.ACCOUNT_MODEL setting.",
                account_model_path
            )
            raise ImportError(f"Import error: {account_model_path}") from None

        self.account_field = (
            payme_settings.get('ACCOUNT_FIELD') or 
            getattr(settings, 'PAYME_ACCOUNT_FIELD', 'id')
        )
        self.amount_field = (
            payme_settings.get('AMOUNT_FIELD') or 
            getattr(settings, 'PAYME_AMOUNT_FIELD', 'amount')
        )
        self.one_time_payment = (
            payme_settings.get('ONE_TIME_PAYMENT') or 
            getattr(settings, 'PAYME_ONE_TIME_PAYMENT', True)
        )

    def post(self, request, **_):
        """
        Handle POST requests from Payme.
        """
        try:
            # Check authorization
            self._check_auth(request)

            # Parse request data
            data = json.loads(request.body.decode('utf-8'))
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
                raise MethodNotFound(f"Method not supported: {method}")

            # Return the result
            return JsonResponse({
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            })

        except PermissionDenied as e:
            return JsonResponse({
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 0,
                'error': {
                    'code': -32504,
                    'message': str(e)
                }
            }, status=200)  # Return 200 status code for all errors

        except (MethodNotFound, UnsupportedMethod) as e:
            return JsonResponse({
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 0,
                'error': {
                    'code': -32601,
                    'message': str(e)
                }
            }, status=200)  # Return 200 status code for all errors

        except AccountNotFound as e:
            return JsonResponse({
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 0,
                'error': {
                    # Code for account not found, in the range -31099 to -31050
                    'code': -31050,
                    'message': str(e)
                }
            }, status=200)  # Return 200 status code for all errors

        except (InvalidAmount, TransactionNotFound) as e:
            return JsonResponse({
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 0,
                'error': {
                    'code': -31001,
                    'message': str(e)
                }
            }, status=200)  # Return 200 status code for all errors

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error in Payme webhook: %s", e)
            return JsonResponse({
                'jsonrpc': '2.0',
                'id': request_id if 'request_id' in locals() else 0,
                'error': {
                    'code': -32400,
                    'message': 'Internal error'
                }
            }, status=200)  # Return 200 status code for all errors

    def _check_auth(self, request):
        """
        Check authorization header.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            raise PermissionDenied("Missing authentication credentials")

        try:
            auth_parts = auth_header.split()
            if len(auth_parts) != 2 or auth_parts[0].lower() != 'basic':
                raise PermissionDenied("Invalid authentication format")

            auth_decoded = base64.b64decode(auth_parts[1]).decode('utf-8')
            _, password = auth_decoded.split(':')  # We only need the password

            if password != self.payme_key:
                raise PermissionDenied("Invalid merchant key")
        except Exception as e:
            logger.error("Authentication error: %s", e)
            raise PermissionDenied("Authentication error") from e

    def _find_account(self, params):
        """
        Find account by parameters.
        """
        account_value = params.get('account', {}).get(self.account_field)
        if not account_value:
            raise AccountNotFound("Account not found in parameters")

        try:
            # Handle special case for 'order_id' field
            # Handle special case for 'order_id' field
            lookup_field = 'id' if self.account_field == 'order_id' else (
                self.account_field
            )

            # Convert account_value to int if needed
            if (lookup_field == 'id' and isinstance(account_value, str)
                    and account_value.isdigit()):
                account_value = int(account_value)

            # Use model manager to find account
            lookup_kwargs = {lookup_field: account_value}
            account = self.account_model._default_manager.get(**lookup_kwargs)
            return account
        except self.account_model.DoesNotExist:
            raise AccountNotFound(
                f"Account with {self.account_field}={account_value} not found"
            ) from None

    def _validate_amount(self, account, amount):
        """
        Validate payment amount.
        """
        # If one_time_payment is disabled, we still validate the amount
        # but we don't require it to match exactly

        expected_amount = Decimal(getattr(account, self.amount_field)) * 100
        received_amount = Decimal(amount)

        # If one_time_payment is enabled, amount must match exactly
        if self.one_time_payment and expected_amount != received_amount:
            raise InvalidAmount(
                f"Invalid amount. Expected: {expected_amount}, "
                f"received: {received_amount}"
            )

        # If one_time_payment is disabled, amount must be positive
        if not self.one_time_payment and received_amount <= 0:
            raise InvalidAmount(
                f"Invalid amount. Amount must be positive, "
                f"received: {received_amount}"
            )

        return True

    def _check_perform_transaction(self, params):
        """
        Handle CheckPerformTransaction method.
        """
        account = self._find_account(params)
        self._validate_amount(account, params.get('amount'))

        # Call the event method
        self.before_check_perform_transaction(params, account)

        return {'allow': True}

    def _create_transaction(self, params):
        """
        Handle CreateTransaction method.
        """
        transaction_id = params.get('id')
        account = self._find_account(params)
        amount = params.get('amount')

        self._validate_amount(account, amount)

        # Check if there's already a transaction for this account
        # with a different transaction_id
        # Only check if one_time_payment is enabled
        if self.one_time_payment:
            # Check for existing transactions in non-final states
            existing_transactions = PaymentTransaction._default_manager.filter(
                gateway=PaymentTransaction.PAYME,
                account_id=account.id
            ).exclude(transaction_id=transaction_id)

            # Filter out transactions in final states
            non_final_transactions = existing_transactions.exclude(
                state__in=[
                    PaymentTransaction.SUCCESSFULLY,
                    PaymentTransaction.CANCELLED
                ]
            )

            if non_final_transactions.exists():
                # If there's already a transaction for this account with a different
                # transaction ID in a non-final state, raise an error
                msg = (
                    f"Account with {self.account_field}={account.id} "
                    "already has a pending transaction"
                )
                raise AccountNotFound(msg)

        # Check for existing transaction with the same transaction_id
        try:
            transaction = PaymentTransaction._default_manager.get(
                gateway=PaymentTransaction.PAYME,
                transaction_id=transaction_id
            )

            # Call the event method
            self.transaction_already_exists(params, transaction)

            return {
                'transaction': transaction.transaction_id,
                'state': transaction.state,
                'create_time': int(transaction.created_at.timestamp() * 1000),
            }
        except PaymentTransaction.DoesNotExist:
            # No existing transaction found, continue with creation
            pass

        # Create new transaction
        transaction = PaymentTransaction.create_transaction(
            gateway=PaymentTransaction.PAYME,
            transaction_id=transaction_id,
            account_id=account.id,
            amount=Decimal(amount) / 100,  # Convert from tiyin to som
            extra_data={
                'account_field': self.account_field,
                'account_value': (params.get('account', {}).get(
                    self.account_field
                )),
                'create_time': params.get('time'),
                'raw_params': params
            }
        )

        # Update state to INITIATING
        transaction.state = PaymentTransaction.INITIATING
        transaction.save()

        # Call the event method
        self.transaction_created(params, transaction, account)

        return {
            'transaction': transaction.transaction_id,
            'state': transaction.state,
            'create_time': int(transaction.created_at.timestamp() * 1000),
        }

    def _perform_transaction(self, params):
        """
        Handle PerformTransaction method.
        """
        transaction_id = params.get('id')

        try:
            transaction = PaymentTransaction._default_manager.get(
                gateway=PaymentTransaction.PAYME,
                transaction_id=transaction_id
            )
        except PaymentTransaction.DoesNotExist:
            raise TransactionNotFound(
                f"Transaction {transaction_id} not found"
            ) from None

        # Mark transaction as paid
        transaction.mark_as_paid()

        # Call the event method
        self.successfully_payment(params, transaction)

        return {
            'transaction': transaction.transaction_id,
            'state': transaction.state,
            'perform_time': (
                int(transaction.performed_at.timestamp() * 1000)
                if transaction.performed_at else 0
            ),
        }

    def _check_transaction(self, params):
        """
        Handle CheckTransaction method.
        """
        transaction_id = params.get('id')

        try:
            transaction = PaymentTransaction._default_manager.get(
                gateway=PaymentTransaction.PAYME,
                transaction_id=transaction_id
            )
        except PaymentTransaction.DoesNotExist:
            raise TransactionNotFound(
                f"Transaction {transaction_id} not found"
            ) from None

        # Call the event method
        self.check_transaction(params, transaction)

        return {
            'transaction': transaction.transaction_id,
            'state': transaction.state,
            'create_time': int(transaction.created_at.timestamp() * 1000),
            'perform_time': (
                int(transaction.performed_at.timestamp() * 1000)
                if transaction.performed_at else 0
            ),
            'cancel_time': (
                int(transaction.cancelled_at.timestamp() * 1000)
                if transaction.cancelled_at else 0
            ),
            'reason': transaction.reason,
        }

    def _cancel_response(self, transaction):
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
            'cancel_time': (
                int(transaction.cancelled_at.timestamp() * 1000)
                if transaction.cancelled_at else 0
            ),
        }

    def _cancel_transaction(self, params):
        """
        Handle CancelTransaction method.
        """
        transaction_id = params.get('id')
        reason = params.get('reason')

        try:
            transaction = PaymentTransaction._default_manager.get(
                gateway=PaymentTransaction.PAYME,
                transaction_id=transaction_id
            )
        except PaymentTransaction.DoesNotExist:
            raise TransactionNotFound(
                f"Transaction {transaction_id} not found"
            ) from None

        # Check if transaction is already cancelled
        if transaction.state == PaymentTransaction.CANCELLED:
            # If transaction is already cancelled, return the existing data
            return self._cancel_response(transaction)

        if transaction.state == PaymentTransaction.INITIATING:
            transaction.mark_as_cancelled_during_init(reason=reason)

        else:
            # Use the mark_as_cancelled method to properly store the reason
            transaction.mark_as_cancelled(reason=reason)

        # Call the event method
        self.cancelled_payment(params, transaction)

        # Return cancel response
        return self._cancel_response(transaction)

    def _get_statement(self, params):
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
        transactions = PaymentTransaction._default_manager.filter(
            gateway=PaymentTransaction.PAYME,
            created_at__gte=from_datetime,
            created_at__lte=to_datetime
        )

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
                'perform_time': (
                    int(transaction.performed_at.timestamp() * 1000)
                    if transaction.performed_at else 0
                ),
                'cancel_time': (
                    int(transaction.cancelled_at.timestamp() * 1000)
                    if transaction.cancelled_at else 0
                ),
                'reason': transaction.reason,
            })

        # Call the event method
        self.get_statement(params, result)

        return {'transactions': result}

    # Event methods that can be overridden by subclasses

    def before_check_perform_transaction(self, params, account):
        """
        Called before checking if a transaction can be performed.

        Args:
            params: Request parameters
            account: Account object
        """
        # This method is meant to be overridden by subclasses

    def transaction_already_exists(self, params, transaction):
        """
        Called when a transaction already exists.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses

    def transaction_created(self, params, transaction, account):
        """
        Called when a transaction is created.

        Args:
            params: Request parameters
            transaction: Transaction object
            account: Account object
        """
        # This method is meant to be overridden by subclasses

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses

    def check_transaction(self, params, transaction):
        """
        Called when checking a transaction.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses

    def cancelled_payment(self, params, transaction):
        """
        Called when a payment is cancelled.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses

    def get_statement(self, params, transactions):
        """
        Called when getting a statement.

        Args:
            params: Request parameters
            transactions: List of transactions
        """
        # This method is meant to be overridden by subclasses


class ClickWebhook(View):
    """
    Base Click webhook handler for Django.

    This class handles webhook requests from the Click payment system.
    You can extend this class and override the event methods to customize
    the behavior.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        paytechuz_settings = getattr(settings, 'PAYTECHUZ', {})
        click_settings = paytechuz_settings.get('CLICK', {})
        
        account_model_path = (
            click_settings.get('ACCOUNT_MODEL') or 
            getattr(settings, 'CLICK_ACCOUNT_MODEL')
        )
        try:
            self.account_model = import_string(account_model_path)
        except ImportError:
            logger.error(
                "Could not import %s. Check PAYTECHUZ.CLICK.ACCOUNT_MODEL setting.",
                account_model_path
            )
            raise ImportError(f"Import error: {account_model_path}") from None

        self.service_id = (
            click_settings.get('SERVICE_ID') or 
            getattr(settings, 'CLICK_SERVICE_ID', '')
        )
        self.secret_key = (
            click_settings.get('SECRET_KEY') or 
            getattr(settings, 'CLICK_SECRET_KEY', '')
        )
        self.commission_percent = (
            click_settings.get('COMMISSION_PERCENT') or 
            getattr(settings, 'CLICK_COMMISSION_PERCENT', 0.0)
        )

    def post(self, request, **_):
        """
        Handle POST requests from Click.
        """
        try:
            # Get parameters from request
            params = request.POST.dict()

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
            except AccountNotFound:
                logger.error("Account not found: %s", merchant_trans_id)
                return JsonResponse({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'error': -5,
                    'error_note': "User not found"
                }, status=200)  # Return 200 status code for all errors

            # Validate amount
            try:
                # Get amount from account and validate
                account_amount = float(getattr(account, 'amount', 0))
                self._validate_amount(amount, account_amount)
            except InvalidAmount as e:
                logger.error("Invalid amount: %s", e)
                return JsonResponse({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'error': -2,
                    'error_note': str(e)
                }, status=200)  # Return 200 status code for all errors

            # Check if transaction already exists
            try:
                transaction = PaymentTransaction._default_manager.get(
                    gateway=PaymentTransaction.CLICK,
                    transaction_id=click_trans_id
                )

                # If transaction is already completed, return success
                if transaction.state == PaymentTransaction.SUCCESSFULLY:
                    # Call the event method
                    self.transaction_already_exists(params, transaction)

                    return JsonResponse({
                        'click_trans_id': click_trans_id,
                        'merchant_trans_id': merchant_trans_id,
                        'merchant_prepare_id': transaction.id,
                        'error': 0,
                        'error_note': "Success"
                    })

                # If transaction is cancelled, return error
                if transaction.state == PaymentTransaction.CANCELLED:
                    return JsonResponse({
                        'click_trans_id': click_trans_id,
                        'merchant_trans_id': merchant_trans_id,
                        'merchant_prepare_id': transaction.id,
                        'error': -9,
                        'error_note': "Transaction cancelled"
                    })
            except PaymentTransaction.DoesNotExist:
                # Transaction doesn't exist, continue with the flow
                pass

            # Handle different actions
            if action == 0:  # Prepare
                # Create transaction
                transaction = PaymentTransaction.create_transaction(
                    gateway=PaymentTransaction.CLICK,
                    transaction_id=click_trans_id,
                    account_id=merchant_trans_id,
                    amount=amount,
                    extra_data={
                        'raw_params': params
                    }
                )

                # Update state to INITIATING
                transaction.state = PaymentTransaction.INITIATING
                transaction.save()

                # Call the event method
                self.transaction_created(params, transaction, account)

                return JsonResponse({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'merchant_prepare_id': transaction.id,
                    'error': 0,
                    'error_note': "Success"
                })

            # Complete action
            if action == 1:
                # Check if error is negative (payment failed)
                is_successful = error >= 0

                try:
                    transaction = PaymentTransaction._default_manager.get(
                        gateway=PaymentTransaction.CLICK,
                        transaction_id=click_trans_id
                    )
                except PaymentTransaction.DoesNotExist:
                    # Create transaction if it doesn't exist
                    transaction = PaymentTransaction.create_transaction(
                        gateway=PaymentTransaction.CLICK,
                        transaction_id=click_trans_id,
                        account_id=merchant_trans_id,
                        amount=amount,
                        extra_data={
                            'raw_params': params
                        }
                    )

                if is_successful:
                    # Mark transaction as paid
                    transaction.mark_as_paid()

                    # Call the event method
                    self.successfully_payment(params, transaction)
                else:
                    # Mark transaction as cancelled
                    transaction.mark_as_cancelled(
                        reason=f"Error code: {error}"
                    )

                    # Call the event method
                    self.cancelled_payment(params, transaction)

                return JsonResponse({
                    'click_trans_id': click_trans_id,
                    'merchant_trans_id': merchant_trans_id,
                    'merchant_prepare_id': transaction.id,
                    'error': 0,
                    'error_note': "Success"
                })

            # Handle unsupported action
            logger.error("Unsupported action: %s", action)
            return JsonResponse({
                'click_trans_id': click_trans_id,
                'merchant_trans_id': merchant_trans_id,
                'error': -3,
                'error_note': "Action not found"
            }, status=200)  # Return 200 status code for all errors

        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error in Click webhook: %s", e)
            return JsonResponse({
                'error': -7,
                'error_note': "Internal error"
            }, status=200)  # Return 200 status code for all errors

    def _check_auth(self, params):
        """
        Check authentication using signature.
        """
        # Check if service_id and secret_key are set
        if not self.service_id or not self.secret_key:
            raise PermissionDenied("Missing required settings: service_id or secret_key")

        if str(params.get("service_id")) != self.service_id:
            raise PermissionDenied("Invalid service ID")

        sign_string = params.get("sign_string")
        sign_time = params.get("sign_time")

        if not sign_string or not sign_time:
            raise PermissionDenied("Missing signature parameters")

        # Prepare signature components; note merchant_prepare_id added compared to your original
        text_parts = [
            str(params.get("click_trans_id") or ""),
            str(params.get("service_id") or ""),
            str(self.secret_key or ""),
            str(params.get("merchant_trans_id") or ""),
            str(params.get("merchant_prepare_id") or ""),  # added here
            str(params.get("amount") or ""),
            str(params.get("action") or ""),
            str(sign_time)
        ]

        # Calculate hash
        calculated_hash = hashlib.md5("".join(text_parts).encode("utf-8")).hexdigest()

        if calculated_hash != sign_string:
            raise PermissionDenied("Invalid signature")


    def _find_account(self, merchant_trans_id):
        """
        Find account by merchant_trans_id.
        """
        try:
            # Convert merchant_trans_id to int if needed
            if (isinstance(merchant_trans_id, str)
                    and merchant_trans_id.isdigit()):
                merchant_trans_id = int(merchant_trans_id)

            # Use model manager to find account
            account = self.account_model._default_manager.get(
                id=merchant_trans_id
            )
            return account
        except self.account_model.DoesNotExist:
            raise AccountNotFound(
                f"Account with id={merchant_trans_id} not found"
            ) from None

    def _validate_amount(self, received_amount, expected_amount):
        """
        Validate payment amount.
        """
        # Add commission if needed
        if self.commission_percent > 0:
            expected_amount = expected_amount * (
                1 + self.commission_percent / 100
            )
            expected_amount = round(expected_amount, 2)

        # Allow small difference due to floating point precision
        if abs(received_amount - expected_amount) > 0.01:
            raise InvalidAmount(
                f"Incorrect amount. Expected: {expected_amount}, "
                f"received: {received_amount}"
            )

    # Event methods that can be overridden by subclasses

    def transaction_already_exists(self, params, transaction):
        """
        Called when a transaction already exists.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses

    def transaction_created(self, params, transaction, account):
        """
        Called when a transaction is created.

        Args:
            params: Request parameters
            transaction: Transaction object
            account: Account object
        """
        # This method is meant to be overridden by subclasses

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses

    def cancelled_payment(self, params, transaction):
        """
        Called when a payment is cancelled.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses


class AtmosWebhook(View):
    """
    Base Atmos webhook handler for Django.

    This class handles webhook requests from the Atmos payment system.
    You can extend this class and override the event methods to customize
    the behavior.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        paytechuz_settings = getattr(settings, 'PAYTECHUZ', {})
        atmos_settings = paytechuz_settings.get('ATMOS', {})

        self.api_key = (
            atmos_settings.get('API_KEY') or
            getattr(settings, 'ATMOS_API_KEY', '')
        )

        account_model_path = (
            atmos_settings.get('ACCOUNT_MODEL') or
            getattr(settings, 'ATMOS_ACCOUNT_MODEL', 'django.contrib.auth.models.User')
        )
        try:
            self.account_model = import_string(account_model_path)
        except ImportError:
            logger.error(
                "Could not import %s. Check PAYTECHUZ.ATMOS.ACCOUNT_MODEL setting.",
                account_model_path
            )
            raise ImportError(f"Import error: {account_model_path}") from None

        self.account_field = (
            atmos_settings.get('ACCOUNT_FIELD') or
            getattr(settings, 'ATMOS_ACCOUNT_FIELD', 'id')
        )

    def post(self, request, **_):
        """
        Handle POST requests from Atmos.
        """
        try:
            # Parse request data
            data = json.loads(request.body.decode('utf-8'))

            # Verify signature
            received_signature = data.get('sign', '')
            if not self._verify_signature(data, received_signature):
                logger.error("Invalid webhook signature")
                return JsonResponse({
                    'status': 0,
                    'message': 'Invalid signature'
                }, status=400)

            # Extract webhook data
            store_id = data.get('store_id')
            transaction_id = data.get('transaction_id')
            amount = data.get('amount')
            invoice = data.get('invoice')
            transaction_time = data.get('transaction_time')

            logger.info(f"Webhook received for transaction {transaction_id}, "
                       f"invoice {invoice}, amount {amount}")

            # Find transaction by invoice (account)
            try:
                transaction = PaymentTransaction._default_manager.get(
                    gateway=PaymentTransaction.ATMOS,
                    account_id=invoice
                )

                # Update transaction with webhook data
                transaction.transaction_id = transaction_id
                transaction.mark_as_paid()

                # Call the event method
                self.successfully_payment(data, transaction)

                return JsonResponse({
                    'status': 1,
                    'message': 'Успешно'
                })

            except PaymentTransaction.DoesNotExist:
                logger.error(f"Transaction not found for invoice: {invoice}")
                return JsonResponse({
                    'status': 0,
                    'message': f'Transaction not found for invoice: {invoice}'
                }, status=400)

        except Exception as e:
            logger.exception("Unexpected error in Atmos webhook: %s", e)
            return JsonResponse({
                'status': 0,
                'message': f'Error: {str(e)}'
            }, status=500)

    def _verify_signature(self, webhook_data, received_signature):
        """
        Verify webhook signature from Atmos.
        """
        # Extract data from webhook
        store_id = str(webhook_data.get('store_id', ''))
        transaction_id = str(webhook_data.get('transaction_id', ''))
        invoice = str(webhook_data.get('invoice', ''))
        amount = str(webhook_data.get('amount', ''))

        # Create signature string: store_id+transaction_id+invoice+amount+api_key
        signature_string = f"{store_id}{transaction_id}{invoice}{amount}{self.api_key}"

        # Generate MD5 hash
        calculated_signature = hashlib.md5(
            signature_string.encode('utf-8')).hexdigest()

        # Compare signatures
        return calculated_signature == received_signature

    # Event methods that can be overridden by subclasses

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        # This method is meant to be overridden by subclasses
