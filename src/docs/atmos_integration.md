# Atmos Payment Gateway Integration

Atmos - O'zbekistondagi mashhur to'lov tizimi. PayTechUZ kutubxonasi Atmos bilan to'liq integratsiyani ta'minlaydi.

## Asosiy xususiyatlar

- ✅ To'lov yaratish (Create Payment)
- ✅ To'lov holatini tekshirish (Check Payment Status)
- ✅ To'lovni bekor qilish (Cancel Payment)
- ✅ Webhook qo'llab-quvvatlash
- ✅ Test va Production muhitlari
- ✅ Django va FastAPI integratsiyalari

## O'rnatish

```bash
pip install paytechuz
```

## Asosiy foydalanish

### 1. Atmos Gateway yaratish

```python
from paytechuz.gateways.atmos import AtmosGateway

# Production muhiti uchun
gateway = AtmosGateway(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret", 
    store_id="your_store_id",
    terminal_id="your_terminal_id",  # ixtiyoriy
    is_test_mode=False
)

# Test muhiti uchun
test_gateway = AtmosGateway(
    consumer_key="test_consumer_key",
    consumer_secret="test_consumer_secret",
    store_id="test_store_id", 
    is_test_mode=True
)
```

### 2. To'lov yaratish

```python
# To'lov yaratish
payment = gateway.create_payment(
    account_id="12345",  # buyurtma ID yoki foydalanuvchi ID
    amount=50000,        # 500.00 so'm (tiyin hisobida)
)

print(f"Transaction ID: {payment['transaction_id']}")
print(f"Payment URL: {payment['payment_url']}")
print(f"Status: {payment['status']}")

# Foydalanuvchini to'lov sahifasiga yo'naltiring
# payment['payment_url'] ga redirect qiling
```

### 3. To'lov holatini tekshirish

```python
# To'lov holatini tekshirish
status = gateway.check_payment("transaction_id_here")

print(f"Transaction ID: {status['transaction_id']}")
print(f"Status: {status['status']}")
print(f"Details: {status['details']}")
```

### 4. To'lovni bekor qilish

```python
# To'lovni bekor qilish
result = gateway.cancel_payment(
    transaction_id="transaction_id_here",
    reason="Mijoz so'rovi bo'yicha"  # ixtiyoriy
)

print(f"Status: {result['status']}")
```

## Webhook qo'llab-quvvatlash

### Webhook Handler

```python
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler

# Webhook handler yaratish
webhook_handler = AtmosWebhookHandler(api_key="your_api_key")

# Webhook ma'lumotlarini qayta ishlash
def process_webhook(request_data):
    try:
        response = webhook_handler.handle_webhook(request_data)
        
        if response['status'] == 1:
            # To'lov muvaffaqiyatli
            transaction_id = request_data.get('transaction_id')
            amount = request_data.get('amount')
            
            # Buyurtma holatini yangilash
            update_order_status(transaction_id, 'paid')
            
        return response
        
    except Exception as e:
        return {
            'status': 0,
            'message': f'Error: {str(e)}'
        }
```

### Webhook imzo tekshirish

```python
# Qo'lda imzo tekshirish
webhook_data = {
    'store_id': '12345',
    'transaction_id': 'txn_123',
    'invoice': 'inv_456', 
    'amount': '50000',
    'sign': 'received_signature'
}

is_valid = webhook_handler.verify_signature(
    webhook_data, 
    webhook_data['sign']
)

if is_valid:
    print("Webhook imzosi to'g'ri")
else:
    print("Webhook imzosi noto'g'ri!")
```

## Constants va Enums

```python
from paytechuz.core.constants import (
    PaymentGateway,
    AtmosEndpoints,
    AtmosNetworks,
    AtmosTransactionStatus
)

# Gateway turi
print(PaymentGateway.ATMOS.value)  # "atmos"

# API endpoints
print(AtmosEndpoints.CREATE_PAYMENT)  # "/merchant/pay/create"
print(AtmosEndpoints.CHECK_PAYMENT)   # "/merchant/pay/get-status"

# Network URLs
print(AtmosNetworks.PROD_NET)         # "https://partner.atmos.uz"
print(AtmosNetworks.PROD_CHECKOUT)    # "https://checkout.pays.uz/invoice/get"

# Transaction statuslari
print(AtmosTransactionStatus.SUCCESS)   # "success"
print(AtmosTransactionStatus.PENDING)   # "pending"
```

## Xatoliklar bilan ishlash

```python
from paytechuz.core.exceptions import (
    PaymentException,
    AuthenticationError,
    TransactionError,
    ExternalServiceError
)

try:
    payment = gateway.create_payment(
        account_id="12345",
        amount=50000
    )
except AuthenticationError as e:
    print(f"Autentifikatsiya xatosi: {e.message}")
except TransactionError as e:
    print(f"Tranzaksiya xatosi: {e.message}")
except ExternalServiceError as e:
    print(f"Tashqi servis xatosi: {e.message}")
except PaymentException as e:
    print(f"Umumiy to'lov xatosi: {e.message}")
```

## Misollar

### Oddiy to'lov jarayoni

```python
from paytechuz.gateways.atmos import AtmosGateway

def create_payment_example():
    # Gateway yaratish
    gateway = AtmosGateway(
        consumer_key="your_key",
        consumer_secret="your_secret",
        store_id="your_store_id",
        is_test_mode=True
    )
    
    try:
        # To'lov yaratish
        payment = gateway.create_payment(
            account_id="order_12345",
            amount=75000  # 750.00 so'm
        )
        
        # Foydalanuvchini to'lov sahifasiga yo'naltirish
        payment_url = payment['payment_url']
        transaction_id = payment['transaction_id']
        
        print(f"To'lov yaratildi!")
        print(f"Transaction ID: {transaction_id}")
        print(f"To'lov URL: {payment_url}")
        
        return payment_url
        
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

# Foydalanish
payment_url = create_payment_example()
if payment_url:
    print(f"Foydalanuvchini {payment_url} ga yo'naltiring")
```

### To'lov holatini kuzatish

```python
import time

def monitor_payment(gateway, transaction_id, max_attempts=10):
    """To'lov holatini kuzatish"""
    
    for attempt in range(max_attempts):
        try:
            status = gateway.check_payment(transaction_id)
            current_status = status['status']
            
            print(f"Urinish {attempt + 1}: Status = {current_status}")
            
            if current_status == 'success':
                print("✅ To'lov muvaffaqiyatli!")
                return True
            elif current_status in ['failed', 'cancelled']:
                print("❌ To'lov muvaffaqiyatsiz!")
                return False
            
            # 30 soniya kutish
            time.sleep(30)
            
        except Exception as e:
            print(f"Xatolik: {e}")
            
    print("⏰ Maksimal urinishlar soni tugadi")
    return False

# Foydalanish
# success = monitor_payment(gateway, "txn_123456")
```

## Muhim eslatmalar

1. **API kalitlari**: Consumer key va secret ni xavfsiz saqlang
2. **Miqdorlar**: Barcha miqdorlar tiyin hisobida (1 so'm = 100 tiyin)
3. **Webhook xavfsizligi**: Har doim webhook imzosini tekshiring
4. **Test muhiti**: Ishlab chiqish jarayonida test muhitidan foydalaning
5. **Xatoliklar**: Barcha API chaqiruvlarini try-catch blokiga o'rang

## Django va FastAPI uchun to'liq konfiguratsiya

### Django settings.py

```python
# settings.py
PAYTECHUZ = {
    'ATMOS': {
        'CONSUMER_KEY': 'sizning_atmos_consumer_key',
        'CONSUMER_SECRET': 'sizning_atmos_consumer_secret',
        'STORE_ID': 'sizning_atmos_store_id',
        'TERMINAL_ID': 'sizning_atmos_terminal_id',  # Ixtiyoriy
        'API_KEY': 'sizning_atmos_api_key',  # Webhook imzo tekshirish uchun
        'ACCOUNT_MODEL': 'myapp.models.Order',  # Buyurtma modeli
        'ACCOUNT_FIELD': 'id',  # Buyurtma ID maydoni
        'IS_TEST_MODE': True,  # Production muhitida False qiling
    }
}
```

### FastAPI environment variables

```python
# .env fayli
ATMOS_CONSUMER_KEY=sizning_atmos_consumer_key
ATMOS_CONSUMER_SECRET=sizning_atmos_consumer_secret
ATMOS_STORE_ID=sizning_atmos_store_id
ATMOS_TERMINAL_ID=sizning_atmos_terminal_id
ATMOS_API_KEY=sizning_atmos_api_key
ATMOS_IS_TEST_MODE=True

# FastAPI da foydalanish
import os
from paytechuz.gateways.atmos import AtmosGateway

atmos = AtmosGateway(
    consumer_key=os.getenv('ATMOS_CONSUMER_KEY'),
    consumer_secret=os.getenv('ATMOS_CONSUMER_SECRET'),
    store_id=os.getenv('ATMOS_STORE_ID'),
    terminal_id=os.getenv('ATMOS_TERMINAL_ID'),
    is_test_mode=os.getenv('ATMOS_IS_TEST_MODE', 'True').lower() == 'true'
)
```

## Qo'shimcha ma'lumot

- [Atmos rasmiy dokumentatsiyasi](https://atmos.uz/developers)
- [PayTechUZ GitHub repository](https://github.com/PayTechUz/paytechuz)
- [Django integratsiyasi](django_integration.md)
- [FastAPI integratsiyasi](fastapi_integration.md)
