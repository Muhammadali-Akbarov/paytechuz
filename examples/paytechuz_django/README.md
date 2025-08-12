# PayTech UZ Django - Order Creation API

Simple Django REST API for creating orders with Payme and Click payment integration.

## Setup

1. **Install dependencies:**
```bash
pip install django djangorestframework paytechuz
```

2. **Run migrations:**
```bash
python manage.py migrate
```

3. **Start server:**
```bash
python manage.py runserver
```

## API Usage

### Create Order

**Endpoint:** `POST /api/orders/create`

**Request:**
```json
{
    "product_name": "Test Product",
    "amount": "100.00",
    "payment_type": "payme"
}
```

**Response:**
```json
{
    "order_id": 1,
    "payment_url": "https://test.paycom.uz/...",
    "payment_type": "payme",
    "amount": "100.00",
    "status": "pending"
}
```

### Payment Types
- `payme` - Payme payment gateway
- `click` - Click payment gateway

## cURL Examples

**Payme:**
```bash
curl -X POST http://127.0.0.1:8000/api/orders/create \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "amount": "100.00",
    "payment_type": "payme"
  }'
```

**Click:**
```bash
curl -X POST http://127.0.0.1:8000/api/orders/create \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "amount": "100.00",
    "payment_type": "click"
  }'
```

## Configuration

Update `backend/settings.py` with your payment gateway credentials:

```python
PAYTECHUZ = {
    'PAYME': {
        'PAYME_ID': 'your_payme_id',
        'PAYME_KEY': 'your_payme_key',
        'IS_TEST_MODE': True,
    },
    'CLICK': {
        'SERVICE_ID': 'your_service_id',
        'MERCHANT_ID': 'your_merchant_id',
        'MERCHANT_USER_ID': 'your_merchant_user_id',
        'SECRET_KEY': 'your_secret_key',
        'IS_TEST_MODE': True,
    }
}
```

## Features

- ✅ Order creation with payment integration
- ✅ Payme payment gateway support
- ✅ Click payment gateway support
- ✅ REST API with JSON responses
- ✅ Input validation
- ✅ Error handling
