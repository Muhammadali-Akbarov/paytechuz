# Payment Integration Example

Modern FastAPI REST API for payment processing with Payme, Click, and Atmos integration.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

### 3. Run Application

```bash
./run.sh
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Orders

**Create Order with Payment**

```http
POST /api/v1/orders
Content-Type: application/json

{
    "product_name": "Test Product",
    "amount": 100.00,
    "payment_method": "payme"
}
```

**Response:**
```json
{
    "id": 1,
    "amount": 100.00,
    "payment_method": "payme",
    "payment_link": "https://test.paycom.uz/..."
}
```

**Fields:**
- `id` - Order ID
- `amount` - Payment amount
- `payment_method` - Gateway name (payme, click, atmos)
- `payment_link` - Payment URL to redirect user

### Webhooks

- `POST /api/v1/webhooks/payme` - Payme webhook
- `POST /api/v1/webhooks/click` - Click webhook
- `POST /api/v1/webhooks/atmos` - Atmos webhook

## cURL Examples

**Payme Payment:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Premium Subscription",
    "amount": 50000.00,
    "payment_method": "payme"
  }'
```

**Response:**
```json
{
    "id": 1,
    "amount": 50000.00,
    "payment_method": "payme",
    "payment_link": "https://test.paycom.uz/..."
}
```

**Click Payment:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Monthly Plan",
    "amount": 25000.00,
    "payment_method": "click"
  }'
```

**Response:**
```json
{
    "id": 2,
    "amount": 25000.00,
    "payment_method": "click",
    "payment_link": "https://my.click.uz/services/pay?..."
}
```

**Atmos Payment:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Annual Subscription",
    "amount": 500000.00,
    "payment_method": "atmos"
  }'
```

**Response:**
```json
{
    "id": 3,
    "amount": 500000.00,
    "payment_method": "atmos",
    "payment_link": "https://partner.atmos.uz/..."
}
```

## Testing Webhooks Locally

Use `jprq` or `ngrok` to expose your local server:

```bash
# Using jprq
jprq http 8000

# Using ngrok
ngrok http 8000
```

Configure webhook URLs in payment gateway admin panels:
- Payme: `https://your-domain.com/api/v1/webhooks/payme`
- Click: `https://your-domain.com/api/v1/webhooks/click`
- Atmos: `https://your-domain.com/api/v1/webhooks/atmos`

## Resources

- [PayTechUZ Documentation](https://github.com/PayTechUz/paytechuz)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Payme Documentation](https://developer.help.paycom.uz/)
- [Click Documentation](https://docs.click.uz/)
- [Atmos Documentation](https://atmos.uz/developers)
