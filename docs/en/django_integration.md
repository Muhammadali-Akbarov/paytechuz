# Django Integration

A guide to installing and configuring the PayTechUZ library in your Django project.

## Installation

```bash
pip install paytechuz[django]
```

## Configuration

### 1. Add the following settings to your settings.py file:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]

# Payme settings
PAYME_ID = 'your_payme_merchant_id'
PAYME_KEY = 'your_payme_merchant_key'
PAYME_ACCOUNT_MODEL = 'your_app.YourModel'  # For example: 'orders.Order'
PAYME_ACCOUNT_FIELD = 'id'  # Field for account identifier
PAYME_AMOUNT_FIELD = 'amount'  # Field for storing payment amount
PAYME_ONE_TIME_PAYMENT = True  # Allow only one payment per account

# Click settings
CLICK_SERVICE_ID = 'your_click_service_id'
CLICK_MERCHANT_ID = 'your_click_merchant_id'
CLICK_SECRET_KEY = 'your_click_secret_key'
CLICK_ACCOUNT_MODEL = 'your_app.YourModel'  # For example: 'orders.Order'
CLICK_COMMISSION_PERCENT = 0.0  # Click commission percentage
```

### 2. Configure URLs

The PayTechUZ library no longer includes URLs. You need to create your own URLs:

```python
# your_app/urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from paytechuz.integrations.django.views import PaymeWebhookView, ClickWebhookView

urlpatterns = [
    # ...
    path('payments/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
```

### 3. Configure the payment process

To configure the payment process, you need to create your model and link it with PayTechUZ:

```python
# your_app/models.py

from django.db import models

class Order(models.Model):
    # Your fields
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.amount}"
```

### 4. Handle payment events

To handle payment events, you can create your own webhook views:

```python
# your_app/views.py

from paytechuz.integrations.django.views import PaymeWebhookView as BasePaymeWebhookView
from paytechuz.integrations.django.views import ClickWebhookView as BaseClickWebhookView
from .models import Order

class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        # Update order status
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.payment_id = transaction.transaction_id
        order.save()

        # Additional logic (e.g., sending email)
        # self.send_payment_confirmation_email(order)

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        # Update order status
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'payment_cancelled'
        order.save()

        # Additional logic
        # self.notify_admin_about_cancelled_payment(order)

class ClickWebhookView(BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        # Update order status
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.payment_id = transaction.transaction_id
        order.save()

        # Additional logic (e.g., sending email)
        # self.send_payment_confirmation_email(order)

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        # Update order status
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'payment_cancelled'
        order.save()

        # Additional logic
        # self.notify_admin_about_cancelled_payment(order)
```
