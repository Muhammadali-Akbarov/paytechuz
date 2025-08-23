# Atmos Payment Gateway Integration

Atmos - O'zbekistondagi mashhur to'lov tizimi.

## O'rnatish

```bash
pip install paytechuz
```

## Asosiy foydalanish

### 1. Gateway yaratish

```python
from paytechuz.gateways.atmos import AtmosGateway

gateway = AtmosGateway(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    store_id="your_store_id",
    is_test_mode=True  # Test uchun True, Production uchun False
)
```

### 2. To'lov yaratish

```python
payment = gateway.create_payment(
    account_id="12345",  # buyurtma ID
    amount=50000,        # 500.00 so'm (tiyin hisobida)
)

print(f"To'lov URL: {payment['payment_url']}")
# Foydalanuvchini payment['payment_url'] ga yo'naltiring
```

### 3. To'lov holatini tekshirish

```python
status = gateway.check_payment("transaction_id")
print(f"Status: {status['status']}")
```

## Webhook

```python
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler

webhook_handler = AtmosWebhookHandler(api_key="your_api_key")

def process_webhook(request_data):
    response = webhook_handler.handle_webhook(request_data)

    if response['status'] == 1:
        # To'lov muvaffaqiyatli
        print("To'lov muvaffaqiyatli!")

    return response
```

## Django integratsiyasi

### Settings.py

```python
INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]

PAYTECHUZ = {
    'ATMOS': {
        'CONSUMER_KEY': 'your_consumer_key',
        'CONSUMER_SECRET': 'your_consumer_secret',
        'STORE_ID': 'your_store_id',
        'API_KEY': 'your_api_key',
        'ACCOUNT_MODEL': 'shop.models.Order',
        'ACCOUNT_FIELD': 'id',
        'IS_TEST_MODE': True,
    }
}
```

### Views.py

```python
from paytechuz.integrations.django.views import BaseAtmosWebhookView
from .models import Order

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

### URLs.py

```python
from django.urls import path
from .views import AtmosWebhookView

urlpatterns = [
    path('webhooks/atmos/', AtmosWebhookView.as_view(), name='atmos_webhook'),
]
```

## FastAPI integratsiyasi

```python
from fastapi import FastAPI, Request
from paytechuz.gateways.atmos import AtmosGateway
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler
import os
import json

app = FastAPI()

# Gateway yaratish
atmos = AtmosGateway(
    consumer_key=os.getenv('ATMOS_CONSUMER_KEY'),
    consumer_secret=os.getenv('ATMOS_CONSUMER_SECRET'),
    store_id=os.getenv('ATMOS_STORE_ID'),
    is_test_mode=True
)

webhook_handler = AtmosWebhookHandler(api_key=os.getenv('ATMOS_API_KEY'))

@app.post("/payment/create")
async def create_payment():
    payment = atmos.create_payment(
        account_id="12345",
        amount=50000
    )
    return {"payment_url": payment['payment_url']}

@app.post("/webhooks/atmos")
async def webhook(request: Request):
    body = await request.body()
    data = json.loads(body.decode('utf-8'))
    return webhook_handler.handle_webhook(data)
```

## Qo'shimcha ma'lumot

- [Atmos rasmiy dokumentatsiyasi](https://atmos.uz/developers)
- [PayTechUZ GitHub repository](https://github.com/PayTechUz/paytechuz)
- [Django integratsiyasi](django_integration.md)
- [FastAPI integratsiyasi](fastapi_integration.md)
