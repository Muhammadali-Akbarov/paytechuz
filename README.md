# paytechuz

[![PyPI version](https://badge.fury.io/py/paytechuz.svg)](https://badge.fury.io/py/paytechuz)
[![Python Versions](https://img.shields.io/pypi/pyversions/paytechuz.svg)](https://pypi.org/project/paytechuz/)
[![Documentation](https://img.shields.io/badge/docs-pay--tech.uz-blue.svg)](https://pay-tech.uz)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PayTechUZ is a unified payment library for integrating with popular payment systems in Uzbekistan. It provides a simple and consistent interface for working with Payme, Click, and Atmos payment gateways.

📖 **[Complete Documentation](https://pay-tech.uz)** | 🚀 **[Quick Start Guide](https://pay-tech.uz/quickstart)**

## Features

- 🔄 **API**: Consistent interface for multiple payment providers
- 🛡️ **Secure**: Built-in security features for payment processing
- 🔌 **Framework Integration**: Native support for Django and FastAPI
- 🌐 **Webhook Handling**: Easy-to-use webhook handlers for payment notifications
- 📊 **Transaction Management**: Automatic transaction tracking and management
- 🧩 **Extensible**: Easy to add new payment providers
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

> 💡 **Need help?** Check out our [complete documentation](https://pay-tech.uz) for detailed guides and examples.

### Generate Payment Links

```python
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.atmos import AtmosGateway

# Initialize Payme gateway
payme = PaymeGateway(
    payme_id="your_payme_id",
    payme_key="your_payme_key",
    is_test_mode=True  # Set to False in production environment
)

# Initialize Click gateway
click = ClickGateway(
    service_id="your_service_id",
    merchant_id="your_merchant_id",
    merchant_user_id="your_merchant_user_id",
    secret_key="your_secret_key",
    is_test_mode=True  # Set to False in production environment
)

# Initialize Atmos gateway
atmos = AtmosGateway(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    store_id="your_store_id",
    terminal_id="your_terminal_id",  # optional
    is_test_mode=True  # Set to False in production environment
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

atmos_payment = atmos.create_payment(
    account_id="order_123",
    amount=150000  # amount in UZS
)
atmos_link = atmos_payment['payment_url']

# Check payment status
status = atmos.check_payment(atmos_payment['transaction_id'])
print(f"Payment status: {status['status']}")

# Cancel payment if needed
if status['status'] == 'pending':
    cancel_result = atmos.cancel_payment(
        transaction_id=atmos_payment['transaction_id'],
        reason="Customer request"
    )
    print(f"Cancellation status: {cancel_result['status']}")
```

### Django Integration

1. Create Order model:

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
```

2. Add to `INSTALLED_APPS` and configure settings:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]

PAYTECHUZ = {
    'PAYME': {
        'PAYME_ID': 'your_payme_id',
        'PAYME_KEY': 'your_payme_key',
        'ACCOUNT_MODEL': 'your_app.models.Order',  # For example: 'orders.models.Order'
        'ACCOUNT_FIELD': 'id',
        'AMOUNT_FIELD': 'amount',
        'ONE_TIME_PAYMENT': True,
        'IS_TEST_MODE': True,  # Set to False in production
    },
    'CLICK': {
        'SERVICE_ID': 'your_service_id',
        'MERCHANT_ID': 'your_merchant_id',
        'MERCHANT_USER_ID': 'your_merchant_user_id',
        'SECRET_KEY': 'your_secret_key',
        'ACCOUNT_MODEL': 'your_app.models.Order',
        'COMMISSION_PERCENT': 0.0,
        'IS_TEST_MODE': True,  # Set to False in production
    },
    'ATMOS': {
        'CONSUMER_KEY': 'your_atmos_consumer_key',
        'CONSUMER_SECRET': 'your_atmos_consumer_secret',
        'STORE_ID': 'your_atmos_store_id',
        'TERMINAL_ID': 'your_atmos_terminal_id',  # Optional
        'API_KEY': 'your_atmos_api_key'
        'ACCOUNT_MODEL': 'your_app.models.Order',
        'ACCOUNT_FIELD': 'id',
        'IS_TEST_MODE': True,  # Set to False in production
    }
}
```

3. Create webhook handlers:

```python
# views.py
from paytechuz.integrations.django.views import (
    BasePaymeWebhookView,
    BaseClickWebhookView,
    BaseAtmosWebhookView
)
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

class ClickWebhookView(BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'cancelled'
        order.save()

class AtmosWebhookView(BaseAtmosWebhookView):
    def successfully_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        order = Order.objects.get(id=transaction.account_id)
        order.status = 'cancelled'
        order.save()
```

4. Add webhook URLs to `urls.py`:

```python
# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PaymeWebhookView, ClickWebhookView, AtmosWebhookView

urlpatterns = [
    # ...
    path('payments/webhook/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/webhook/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
    path('payments/webhook/atmos/', csrf_exempt(AtmosWebhookView.as_view()), name='atmos_webhook'),
]
```

### FastAPI Integration

1. Set up database models:

```python
from datetime import datetime, timezone

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime

from paytechuz.integrations.fastapi import Base as PaymentsBase
from paytechuz.integrations.fastapi.models import run_migrations


# Create database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./payments.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create base declarative class
Base = declarative_base()

# Create Order model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Create payment tables using run_migrations
run_migrations(engine)

# Create Order table
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

2. Create webhook handlers:

```python
from fastapi import FastAPI, Request, Depends

from sqlalchemy.orm import Session

from paytechuz.integrations.fastapi import PaymeWebhookHandler, ClickWebhookHandler
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler


app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

class CustomClickWebhookHandler(ClickWebhookHandler):
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
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomPaymeWebhookHandler(
        db=db,
        payme_id="your_merchant_id",
        payme_key="your_merchant_key",
        account_model=Order,
        account_field='id',
        amount_field='amount'
    )
    return await handler.handle_webhook(request)

@app.post("/payments/click/webhook")
async def click_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomClickWebhookHandler(
        db=db,
        service_id="your_service_id",
        secret_key="your_secret_key",
        account_model=Order
    )
    return await handler.handle_webhook(request)

@app.post("/payments/atmos/webhook")
async def atmos_webhook(request: Request, db: Session = Depends(get_db)):
    import json

    # Atmos webhook handler
    atmos_handler = AtmosWebhookHandler(api_key="your_atmos_api_key")

    try:
        # Get request body
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))

        # Process webhook
        response = atmos_handler.handle_webhook(webhook_data)

        if response['status'] == 1:
            # Payment successful
            invoice = webhook_data.get('invoice')

            # Update order status
            order = db.query(Order).filter(Order.id == invoice).first()
            if order:
                order.status = "paid"
                db.commit()

        return response

    except Exception as e:
        return {
            'status': 0,
            'message': f'Error: {str(e)}'
        }
```

## Documentation

Detailed documentation is available in multiple languages:

- 📖 [English Documentation](src/docs/en/index.md)
- 📖 [O'zbek tilidagi hujjatlar](src/docs/index.md)

### Framework-Specific Documentation

- [Django Integration Guide](src/docs/en/django_integration.md) | [Django integratsiyasi bo'yicha qo'llanma](src/docs/django_integration.md)
- [FastAPI Integration Guide](src/docs/en/fastapi_integration.md) | [FastAPI integratsiyasi bo'yicha qo'llanma](src/docs/fastapi_integration.md)
- [Atmos Integration Guide](src/docs/en/atmos_integration.md) | [Atmos integratsiyasi bo'yicha qo'llanma](src/docs/atmos_integration.md)

## Supported Payment Systems

- **Payme** - [Official Website](https://payme.uz)
- **Click** - [Official Website](https://click.uz)
- **Atmos** - [Official Website](https://atmos.uz)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

📖 **Documentation:** [pay-tech.uz](https://pay-tech.uz)  
🐛 **Issues:** [GitHub Issues](https://github.com/PayTechUz/paytechuz-py/issues)  
💬 **Support:** [Telegram](https://t.me/paytechuz)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
