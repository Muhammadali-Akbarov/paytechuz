# PayTechUZ Django Integration

PayTechUZ library provides full integration with Django and supports Payme, Click, and Atmos payment systems.

## Installation

1. Install the library with Django support:

```bash
pip install paytechuz[django]
```

2. Add PayTechUZ to your Django project's `settings.py` file:

```python
INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]
```

3. Run migrations:

```bash
python manage.py migrate
```

## Create Order Model

Create a model for orders:

```python
# models.py
from django.db import models
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),
    )

    product_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.product_name} ({self.amount})"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
```

After creating the model, create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Settings Configuration

Add PAYTECHUZ settings to your `settings.py` file. Use the unified configuration format for all payment systems:

```python
# settings.py
PAYTECHUZ = {
    'PAYME': {
        'PAYME_ID': 'your_payme_merchant_id',
        'PAYME_KEY': 'your_payme_merchant_key',
        'ACCOUNT_MODEL': 'your_app.models.Order',  # Example: 'shop.models.Order'
        'ACCOUNT_FIELD': 'id',
        'AMOUNT_FIELD': 'amount',
        'ONE_TIME_PAYMENT': True,
        'IS_TEST_MODE': True,  # Set to False in production
    },
    'CLICK': {
        'SERVICE_ID': 'your_click_service_id',
        'MERCHANT_ID': 'your_click_merchant_id',
        'MERCHANT_USER_ID': 'your_click_merchant_user_id',
        'SECRET_KEY': 'your_click_secret_key',
        'ACCOUNT_MODEL': 'your_app.models.Order',
        'COMMISSION_PERCENT': 0.0,
        'IS_TEST_MODE': True,  # Set to False in production
    },
    'ATMOS': {
        'CONSUMER_KEY': 'your_atmos_consumer_key',
        'CONSUMER_SECRET': 'your_atmos_consumer_secret',
        'STORE_ID': 'your_atmos_store_id',
        'TERMINAL_ID': 'your_atmos_terminal_id',  # Optional
        'API_KEY': 'your_atmos_api_key',  # For webhook signature verification
        'ACCOUNT_MODEL': 'your_app.models.Order',
        'ACCOUNT_FIELD': 'id',
        'IS_TEST_MODE': True,  # Set to False in production
    }
}
```

## Configure URLs

Add webhook URLs to your project's main `urls.py` file:

```python
# urls.py
from django.urls import path
from .views import PaymeWebhookView, ClickWebhookView, AtmosWebhookView

urlpatterns = [
    # ...
    # PayTechUZ webhook URLs
    path('webhooks/payme/', PaymeWebhookView.as_view(), name='payme_webhook'),
    path('webhooks/click/', ClickWebhookView.as_view(), name='click_webhook'),
    path('webhooks/atmos/', AtmosWebhookView.as_view(), name='atmos_webhook'),
]
```

## Create Webhook Views

Create custom webhook views for each payment system:

```python
# views.py
from paytechuz.integrations.django.views import (
    BasePaymeWebhookView,
    BaseClickWebhookView,
    BaseAtmosWebhookView
)
from .models import Order
import logging

logger = logging.getLogger(__name__)

class PaymeWebhookView(BasePaymeWebhookView):
    """Custom webhook view for Payme"""

    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
            logger.info(f"Payme: Order #{order.id} successfully paid")
        except Order.DoesNotExist:
            logger.error(f"Payme: Order not found: {transaction.account_id}")

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'cancelled'
            order.save()
            logger.info(f"Payme: Order #{order.id} cancelled")
        except Order.DoesNotExist:
            logger.error(f"Payme: Order not found: {transaction.account_id}")

class ClickWebhookView(BaseClickWebhookView):
    """Custom webhook view for Click"""

    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
            logger.info(f"Click: Order #{order.id} successfully paid")
        except Order.DoesNotExist:
            logger.error(f"Click: Order not found: {transaction.account_id}")

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'cancelled'
            order.save()
            logger.info(f"Click: Order #{order.id} cancelled")
        except Order.DoesNotExist:
            logger.error(f"Click: Order not found: {transaction.account_id}")

class AtmosWebhookView(BaseAtmosWebhookView):
    """Custom webhook view for Atmos"""

    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
            logger.info(f"Atmos: Order #{order.id} successfully paid")
        except Order.DoesNotExist:
            logger.error(f"Atmos: Order not found: {transaction.account_id}")

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'cancelled'
            order.save()
            logger.info(f"Atmos: Order #{order.id} cancelled")
        except Order.DoesNotExist:
            logger.error(f"Atmos: Order not found: {transaction.account_id}")
```

## Create Payment Links

Example of creating payment links in a Django view:

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.atmos import AtmosGateway
from .models import Order

def create_payment_link(request, order_id):
    """Create payment link for an order"""
    order = get_object_or_404(Order, id=order_id)
    payment_method = request.GET.get('method', 'payme')  # payme, click, atmos

    try:
        if payment_method == 'payme':
            # Create Payme payment link
            payme_config = settings.PAYTECHUZ['PAYME']
            payme = PaymeGateway(
                payme_id=payme_config['PAYME_ID'],
                payme_key=payme_config['PAYME_KEY'],
                is_test_mode=payme_config.get('IS_TEST_MODE', True)
            )
            payment_link = payme.create_payment(
                id=order.id,
                amount=int(order.amount * 100),  # Payme works with tiyin
                return_url=request.build_absolute_uri('/payment/success/')
            )

        elif payment_method == 'click':
            # Create Click payment link
            click_config = settings.PAYTECHUZ['CLICK']
            click = ClickGateway(
                service_id=click_config['SERVICE_ID'],
                merchant_id=click_config['MERCHANT_ID'],
                merchant_user_id=click_config['MERCHANT_USER_ID'],
                secret_key=click_config['SECRET_KEY'],
                is_test_mode=click_config.get('IS_TEST_MODE', True)
            )
            payment_link = click.create_payment(
                id=order.id,
                amount=order.amount,
                return_url=request.build_absolute_uri('/payment/success/'),
                description=f"Payment for order #{order.id}"
            )

        elif payment_method == 'atmos':
            # Create Atmos payment link
            atmos_config = settings.PAYTECHUZ['ATMOS']
            atmos = AtmosGateway(
                consumer_key=atmos_config['CONSUMER_KEY'],
                consumer_secret=atmos_config['CONSUMER_SECRET'],
                store_id=atmos_config['STORE_ID'],
                terminal_id=atmos_config.get('TERMINAL_ID'),
                is_test_mode=atmos_config.get('IS_TEST_MODE', True)
            )
            atmos_payment = atmos.create_payment(
                account_id=order.id,
                amount=int(order.amount * 100)  # Atmos works with tiyin
            )
            payment_link = atmos_payment['payment_url']

        else:
            return JsonResponse({'error': 'Invalid payment method'}, status=400)

        return JsonResponse({
            'success': True,
            'payment_url': payment_link,
            'order_id': order.id,
            'amount': order.amount,
            'method': payment_method
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def payment_success(request):
    """Called when payment is successful"""
    return render(request, 'payment/success.html')
```

## Configure Webhook URLs

Set webhook URLs in the payment systems' admin panels:

### Payme
```
https://yourdomain.com/webhooks/payme/
```

### Click
```
https://yourdomain.com/webhooks/click/
```

### Atmos
```
https://yourdomain.com/webhooks/atmos/
```

## Additional Information

- [Detailed Atmos integration guide](atmos_integration.md)
- [FastAPI integration](fastapi_integration.md)
- [PayTechUZ GitHub repository](https://github.com/PayTechUz/paytechuz)
