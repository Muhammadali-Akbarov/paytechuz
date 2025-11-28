"""
Django views for PayTechUZ.
"""
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .webhooks import PaymeWebhook, ClickWebhook, AtmosWebhook

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class BasePaymeWebhookView(PaymeWebhook):
    """
    Default Payme webhook view.

    This view handles webhook requests from the Payme payment system.
    You can extend this class and override the event methods to customize
    the behavior.

    Example:
    ```python
    from paytechuz.integrations.django.views import PaymeWebhookView

    class CustomPaymeWebhookView(PaymeWebhookView):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")

            # Update your order status
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
    ```
    """

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        logger.info(f"Payme payment successful: {transaction.transaction_id}")

    def cancelled_payment(self, params, transaction):
        """
        Called when a payment is cancelled.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        logger.info(f"Payme payment cancelled: {transaction.transaction_id}")

@method_decorator(csrf_exempt, name='dispatch')
class BaseClickWebhookView(ClickWebhook):
    """
    Default Click webhook view.

    This view handles webhook requests from the Click payment system.
    You can extend this class and override the event methods to customize
    the behavior.

    Example:
    ```python
    from paytechuz.integrations.django.views import ClickWebhookView

    class CustomClickWebhookView(ClickWebhookView):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")

            # Update your order status
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
    ```
    """

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        logger.info(f"Click payment successful: {transaction.transaction_id}")

    def cancelled_payment(self, params, transaction):
        """
        Called when a payment is cancelled.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        logger.info(f"Click payment cancelled: {transaction.transaction_id}")


@method_decorator(csrf_exempt, name='dispatch')
class BaseAtmosWebhookView(AtmosWebhook):
    """
    Default Atmos webhook view.

    This view handles webhook requests from the Atmos payment system.
    You can extend this class and override the event methods to customize
    the behavior.

    Example:
    ```python
    from paytechuz.integrations.django.views import AtmosWebhookView

    class CustomAtmosWebhookView(AtmosWebhookView):
        def successfully_payment(self, params, transaction):
            # Your custom logic here
            print(f"Payment successful: {transaction.transaction_id}")

            # Update your order status
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
    ```
    """

    def successfully_payment(self, params, transaction):
        """
        Called when a payment is successful.

        Args:
            params: Request parameters
            transaction: Transaction object
        """
        logger.info(f"Atmos payment successful: {transaction.transaction_id}")
