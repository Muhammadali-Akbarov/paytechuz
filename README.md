# paytechuz

paytechuz is a unified payment library for integration with popular payment systems in Uzbekistan (Payme and Click).

[![PyPI version](https://badge.fury.io/py/paytechuz.svg)](https://badge.fury.io/py/paytechuz)
[![Python Versions](https://img.shields.io/pypi/pyversions/paytechuz.svg)](https://pypi.org/project/paytechuz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

To install paytechuz with all dependencies:

```bash
pip install paytechuz
```

For specific framework support:

```bash
# For Django
pip install paytechuz[django]

# For FastAPI
pip install paytechuz[fastapi]
```

## Quick Start

### Django Integration

1. Add the app to your `INSTALLED_APPS`:

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
```

2. Set up the webhook URLs:

```python
# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from your_app.views import PaymeWebhookView, ClickWebhookView


urlpatterns = [
    # ...
    path('payments/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
```

3. Create custom webhook handlers:

```python
# views.py
from paytechuz.integrations.django.views import PaymeWebhookView as BasePaymeWebhookView
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
```

### FastAPI Integration

1. Create a custom webhook handler:

```python
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.models import Order
from paytechuz.integrations.fastapi import PaymeWebhookHandler

# Payme configuration
PAYME_ID = 'your_payme_id'
PAYME_KEY = 'your_payme_key'

class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction) -> None:
        """Called when payment is successful"""
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "paid"
            self.db.commit()

    def cancelled_payment(self, params, transaction) -> None:
        """Called when payment is cancelled"""
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "cancelled"
            self.db.commit()
```

2. Create a webhook endpoint:

```python
router = APIRouter()

@router.post("/payments/payme/webhook")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Payme webhook requests"""
    handler = CustomPaymeWebhookHandler(
        db=db,
        payme_id=PAYME_ID,
        payme_key=PAYME_KEY,
        account_model=Order,
        account_field="id",
        amount_field="amount",
        one_time_payment=False
    )
    result = await handler.handle_webhook(request)
    return result
```

## Documentation

For detailed documentation, see:

- [English Documentation](paytechuz/docs/en/index.md)
- [O'zbek tilidagi hujjatlar](paytechuz/docs/index.md)
