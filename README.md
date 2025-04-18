# PayTechUZ

[![PyPI version](https://badge.fury.io/py/paytechuz.svg)](https://badge.fury.io/py/paytechuz)
[![Python Versions](https://img.shields.io/pypi/pyversions/paytechuz.svg)](https://pypi.org/project/paytechuz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
## Installation

### Basic Installation

```bash
pip install paytechuz
```

### Framework-Specific Installation

```bash
# For Django
pip install paytechuz[django]

# For FastAPI
pip install paytechuz[fastapi]
```

## Quick Start

### Generate Payment Links

```python
from paytechuz import create_gateway, PaymentGateway

# Initialize gateways
payme = create_gateway(PaymentGateway.PAYME.value,
    payme_id="your_payme_id",
    payme_key="your_payme_key",
    is_test_mode=True
)

click = create_gateway(PaymentGateway.CLICK.value,
    service_id="your_service_id",
    merchant_id="your_merchant_id",
    merchant_user_id="your_merchant_user_id",
    secret_key="your_secret_key",
    is_test_mode=True
)

# Generate payment links
payme_link = payme.create_payment(
    id="order_123",
    amount=150000,  # amount in UZS
    return_url="https://example.com/return"
)

click_link = click.create_payment(
    id="order_123",
    amount=150000,  # amount in UZS
    description="Test payment",
    return_url="https://example.com/return"
)
```

### Django Integration

1. Add to `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]

PAYME_ID = 'your_payme_merchant_id'
PAYME_KEY = 'your_payme_merchant_key'
PAYME_ACCOUNT_MODEL = 'your_app.models.YourModel'  # For example: 'orders.models.Order'
PAYME_ACCOUNT_FIELD = 'id'
PAYME_AMOUNT_FIELD = 'amount'  # Field for storing payment amount
PAYME_ONE_TIME_PAYMENT = True  # Allow only one payment per account

CLICK_SERVICE_ID = 'your_click_service_id'
CLICK_MERCHANT_ID = 'your_click_merchant_id'
CLICK_SECRET_KEY = 'your_click_secret_key'
CLICK_ACCOUNT_MODEL = 'your_app.models.YourModel'
CLICK_COMMISSION_PERCENT = 0.0
```

2. Create webhook handlers:

```python
# views.py
from paytechuz.integrations.django.views import BasePaymeWebhookView
from .models import Order

class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'cancelled'
        order.save()
```

3. Add webhook URLs to `urls.py`:

```python
# urls.py
from django.urls import path
from .views import PaymeWebhookView

urlpatterns = [
    # ...
    path('payments/webhook/payme/', PaymeWebhookView.as_view(), name='payme_webhook'),
]
```

### FastAPI Integration

1. Create webhook handler:

```python
from fastapi import FastAPI, Request
from paytechuz.integrations.fastapi import PaymeWebhookHandler

app = FastAPI()

class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction):
        # Handle successful payment
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = "paid"
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        # Handle cancelled payment
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = "cancelled"
        self.db.commit()

@app.post("/payments/payme/webhook")
async def payme_webhook(request: Request):
    handler = CustomPaymeWebhookHandler(
        payme_id="your_merchant_id",
        payme_key="your_merchant_key"
    )
    return await handler.handle_webhook(request)
```

## Documentation

Detailed documentation is available in multiple languages:

- 📖 [English Documentation](docs/en/index.md)
- 📖 [O'zbek tilidagi hujjatlar](docs/uz/index.md)
