# PayTechUZ Django Integration

## Installation

1. Install the library:

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

## Basic Configuration

Add the following settings to your `settings.py` file:

```python
# Payme settings
PAYME_ID = 'your_payme_merchant_id'
PAYME_KEY = 'your_payme_merchant_key'
PAYME_ACCOUNT_MODEL = 'your_app.Order'  # For example: 'orders.Order'
PAYME_ACCOUNT_FIELD = 'id'
PAYME_AMOUNT_FIELD = 'amount'

# Click settings
CLICK_SERVICE_ID = 'your_click_service_id'
CLICK_MERCHANT_ID = 'your_click_merchant_id'
CLICK_SECRET_KEY = 'your_click_secret_key'
CLICK_ACCOUNT_MODEL = 'your_app.Order'
```

## Configure URLs

```python
# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from paytechuz.integrations.django.views import PaymeWebhookView, ClickWebhookView

urlpatterns = [
    # ...
    path('payments/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
```

## Handle Payment Events

```python
# views.py
from paytechuz.integrations.django.views import PaymeWebhookView as BasePaymeWebhookView
from paytechuz.integrations.django.views import ClickWebhookView as BaseClickWebhookView
from .models import Order

class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'cancelled'
        order.save()

class ClickWebhookView(BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'cancelled'
        order.save()
```

## Create Payment Links

```python
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

# Get the order
order = Order.objects.get(id=1)

# Generate Payme payment link
payme = PaymeGateway(
    payme_id='your_payme_id',
    payme_key='your_payme_key',
    is_test_mode=True  # Set to False in production environment
)
payme_link = payme.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return"
)

# Generate Click payment link
click = ClickGateway(
    service_id='your_service_id',
    merchant_id='your_merchant_id',
    merchant_user_id='your_merchant_user_id',
    secret_key='your_secret_key',
    is_test_mode=True  # Set to False in production environment
)
# Click.create_payment() directly returns the payment URL
click_link = click.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return",
    description="Payment for order"
)
```
