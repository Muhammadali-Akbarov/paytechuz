"""
Base classes for payment gateways.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union


class BasePaymentGateway(ABC):
    """
    Base class for all payment gateways.

    This abstract class defines the common interface that all payment gateways
    must implement. It provides a consistent API for creating, checking, and
    canceling payments regardless of the underlying payment provider.
    """

    def __init__(self, is_test_mode: bool = False):
        """
        Initialize the payment gateway.

        Args:
            is_test_mode (bool): Whether to use the test environment
        """
        self.is_test_mode = is_test_mode

    @abstractmethod
    def create_payment(
        self,
        id: Union[int, str],
        amount: Union[int, float, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a payment.

        Args:
            id: The account ID or order ID
            amount: The payment amount
            **kwargs: Additional parameters specific to the payment gateway

        Returns:
            Dict containing payment details including transaction ID
        """
        raise NotImplementedError

    @abstractmethod
    def check_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Check payment status.

        Args:
            transaction_id: The transaction ID to check

        Returns:
            Dict containing payment status and details
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError


class BaseWebhookHandler(ABC):
    """
    Base class for payment gateway webhook handlers.

    This abstract class defines the common interface for handling webhook
    callbacks from payment gateways.
    """

    @abstractmethod
    def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook data from payment gateway.

        Args:
            data: The webhook data received from the payment gateway

        Returns:
            Dict containing the response to be sent back to the payment gateway
        """
        raise NotImplementedError
