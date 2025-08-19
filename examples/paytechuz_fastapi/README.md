# PayTech UZ FastAPI - Order Creation API

Simple FastAPI REST API for creating orders with Payme, Click, and Atmos payment integration.

## Setup

1. **Install dependencies:**
```bash
pip install fastapi uvicorn sqlalchemy paytechuz
```

2. **Start server:**
```bash
python main.py
# or
uvicorn main:app --reload
```

## API Usage

### Create Order

**Endpoint:** `POST /orders/`

**Request:**
```json
{
    "product_name": "Test Product",
    "amount": 100.00,
    "payment_method": "payme",
    "return_url": "https://example.com/return"
}
```

**Response:**
```json
{
    "id": 1,
    "product_name": "Test Product",
    "amount": 100.00,
    "status": "pending",
    "created_at": "2024-01-01T12:00:00",
    "payment_method": "payme",
    "payment_link": "https://test.paycom.uz/..."
}
```

### Payment Methods
- `payme` - Payme payment gateway
- `click` - Click payment gateway
- `atmos` - Atmos payment gateway

## cURL Examples

**Payme:**
```bash
curl -X POST http://127.0.0.1:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "amount": 100.00,
    "payment_method": "payme",
    "return_url": "https://example.com/return"
  }'
```

**Click:**
```bash
curl -X POST http://127.0.0.1:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "amount": 100.00,
    "payment_method": "click",
    "return_url": "https://example.com/return"
  }'
```

**Atmos:**
```bash
curl -X POST http://127.0.0.1:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "amount": 100.00,
    "payment_method": "atmos",
    "return_url": "https://example.com/return"
  }'
```

## Webhook Endpoints

The API provides webhook endpoints for each payment gateway:

- `POST /payments/payme/webhook` - Payme webhook
- `POST /payments/click/webhook` - Click webhook
- `POST /payments/atmos/webhook` - Atmos webhook

## Configuration

Update the gateway configurations in `main.py`:

```python
# Payme configuration
payme = PaymeGateway(
    payme_id="your_payme_id",
    payme_key="your_payme_key",
    is_test_mode=True
)

# Click configuration
click = ClickGateway(
    service_id="your_service_id",
    merchant_id="your_merchant_id",
    merchant_user_id="your_merchant_user_id",
    secret_key="your_secret_key",
    is_test_mode=True
)

# Atmos configuration
atmos = AtmosGateway(
    consumer_key="your_atmos_consumer_key",
    consumer_secret="your_atmos_consumer_secret",
    store_id="your_atmos_store_id",
    terminal_id="your_atmos_terminal_id",  # Optional
    is_test_mode=True
)
```

## Environment Variables

For production, use environment variables:

```bash
# .env file
PAYME_ID=your_payme_id
PAYME_KEY=your_payme_key

CLICK_SERVICE_ID=your_service_id
CLICK_MERCHANT_ID=your_merchant_id
CLICK_MERCHANT_USER_ID=your_merchant_user_id
CLICK_SECRET_KEY=your_secret_key

ATMOS_CONSUMER_KEY=your_atmos_consumer_key
ATMOS_CONSUMER_SECRET=your_atmos_consumer_secret
ATMOS_STORE_ID=your_atmos_store_id
ATMOS_TERMINAL_ID=your_atmos_terminal_id
ATMOS_API_KEY=your_atmos_api_key

IS_TEST_MODE=True
```

## Features

- ✅ Order creation with payment integration
- ✅ Payme payment gateway support
- ✅ Click payment gateway support
- ✅ Atmos payment gateway support
- ✅ FastAPI with automatic API documentation
- ✅ SQLAlchemy ORM integration
- ✅ Pydantic models for validation
- ✅ Webhook handlers for all payment gateways
- ✅ Error handling and validation
- ✅ SQLite database (easily configurable)

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Database

The example uses SQLite database (`payments.db`) which is automatically created when you run the application.

## Testing Webhooks

To test webhooks locally, you can use tools like ngrok:

```bash
# Install ngrok
npm install -g ngrok

# Expose local server
ngrok http 8000

# Use the ngrok URL for webhook configuration
# Example: https://abc123.ngrok.io/payments/payme/webhook
```

## Project Structure

```
paytechuz_fastapi/
├── main.py                 # Main FastAPI application
├── app/
│   ├── __init__.py
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   ├── typing.py           # Pydantic models
│   └── webhook_handlers.py # Custom webhook handlers
├── payments.db             # SQLite database
└── README.md              # This file
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request** - Invalid input data
- **404 Not Found** - Order not found
- **500 Internal Server Error** - Payment gateway errors

Example error response:
```json
{
    "detail": "Invalid payment method. Use 'payme', 'click', or 'atmos'"
}
```

## Next Steps

1. Configure your payment gateway credentials
2. Set up webhook URLs in your payment gateway admin panels
3. Test the integration with real payment data
4. Deploy to production with proper environment variables
5. Monitor webhook events and payment statuses

For more information, visit:
- [PayTechUZ Documentation](https://github.com/PayTechUz/paytechuz)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Payme Documentation](https://developer.help.paycom.uz/)
- [Click Documentation](https://docs.click.uz/)
- [Atmos Documentation](https://atmos.uz/developers)
