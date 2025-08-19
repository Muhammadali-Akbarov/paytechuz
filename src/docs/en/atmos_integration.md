# Atmos Payment Gateway Integration

Atmos is a popular payment system in Uzbekistan. PayTechUZ library provides full integration with Atmos.

## Key Features

- ✅ Create Payment
- ✅ Check Payment Status
- ✅ Cancel Payment
- ✅ Webhook Support
- ✅ Test and Production Environments
- ✅ Django and FastAPI Integrations

## Installation

```bash
pip install paytechuz
```

## Basic Usage

### 1. Create Atmos Gateway

```python
from paytechuz.gateways.atmos import AtmosGateway

# For production environment
gateway = AtmosGateway(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret", 
    store_id="your_store_id",
    terminal_id="your_terminal_id",  # optional
    is_test_mode=False
)

# For test environment
test_gateway = AtmosGateway(
    consumer_key="test_consumer_key",
    consumer_secret="test_consumer_secret",
    store_id="test_store_id", 
    is_test_mode=True
)
```

### 2. Create Payment

```python
# Create payment
payment = gateway.create_payment(
    account_id="12345",  # order ID or user ID
    amount=50000,        # 500.00 UZS (in tiyin)
)

print(f"Transaction ID: {payment['transaction_id']}")
print(f"Payment URL: {payment['payment_url']}")
print(f"Status: {payment['status']}")

# Redirect user to payment page
# Redirect to payment['payment_url']
```

### 3. Check Payment Status

```python
# Check payment status
status = gateway.check_payment("transaction_id_here")

print(f"Transaction ID: {status['transaction_id']}")
print(f"Status: {status['status']}")
print(f"Details: {status['details']}")
```

### 4. Cancel Payment

```python
# Cancel payment
result = gateway.cancel_payment(
    transaction_id="transaction_id_here",
    reason="Customer request"  # optional
)

print(f"Status: {result['status']}")
```

## Webhook Support

### Webhook Handler

```python
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler

# Create webhook handler
webhook_handler = AtmosWebhookHandler(api_key="your_api_key")

# Process webhook data
def process_webhook(request_data):
    try:
        response = webhook_handler.handle_webhook(request_data)
        
        if response['status'] == 1:
            # Payment successful
            transaction_id = request_data.get('transaction_id')
            amount = request_data.get('amount')
            
            # Update order status
            update_order_status(transaction_id, 'paid')
            
        return response
        
    except Exception as e:
        return {
            'status': 0,
            'message': f'Error: {str(e)}'
        }
```

### Webhook Signature Verification

```python
# Manual signature verification
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
    print("Webhook signature is valid")
else:
    print("Invalid webhook signature!")
```

## Constants and Enums

```python
from paytechuz.core.constants import (
    PaymentGateway,
    AtmosEndpoints,
    AtmosNetworks,
    AtmosTransactionStatus
)

# Gateway type
print(PaymentGateway.ATMOS.value)  # "atmos"

# API endpoints
print(AtmosEndpoints.CREATE_PAYMENT)  # "/merchant/pay/create"
print(AtmosEndpoints.CHECK_PAYMENT)   # "/merchant/pay/get-status"

# Network URLs
print(AtmosNetworks.PROD_NET)         # "https://partner.atmos.uz"
print(AtmosNetworks.PROD_CHECKOUT)    # "https://checkout.pays.uz/invoice/get"

# Transaction statuses
print(AtmosTransactionStatus.SUCCESS)   # "success"
print(AtmosTransactionStatus.PENDING)   # "pending"
```

## Error Handling

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
    print(f"Authentication error: {e.message}")
except TransactionError as e:
    print(f"Transaction error: {e.message}")
except ExternalServiceError as e:
    print(f"External service error: {e.message}")
except PaymentException as e:
    print(f"General payment error: {e.message}")
```

## Examples

### Simple Payment Flow

```python
from paytechuz.gateways.atmos import AtmosGateway

def create_payment_example():
    # Create gateway
    gateway = AtmosGateway(
        consumer_key="your_key",
        consumer_secret="your_secret",
        store_id="your_store_id",
        is_test_mode=True
    )
    
    try:
        # Create payment
        payment = gateway.create_payment(
            account_id="order_12345",
            amount=75000  # 750.00 UZS
        )
        
        # Redirect user to payment page
        payment_url = payment['payment_url']
        transaction_id = payment['transaction_id']
        
        print(f"Payment created!")
        print(f"Transaction ID: {transaction_id}")
        print(f"Payment URL: {payment_url}")
        
        return payment_url
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Usage
payment_url = create_payment_example()
if payment_url:
    print(f"Redirect user to {payment_url}")
```

### Payment Status Monitoring

```python
import time

def monitor_payment(gateway, transaction_id, max_attempts=10):
    """Monitor payment status"""
    
    for attempt in range(max_attempts):
        try:
            status = gateway.check_payment(transaction_id)
            current_status = status['status']
            
            print(f"Attempt {attempt + 1}: Status = {current_status}")
            
            if current_status == 'success':
                print("✅ Payment successful!")
                return True
            elif current_status in ['failed', 'cancelled']:
                print("❌ Payment failed!")
                return False
            
            # Wait 30 seconds
            time.sleep(30)
            
        except Exception as e:
            print(f"Error: {e}")
            
    print("⏰ Maximum attempts reached")
    return False

# Usage
# success = monitor_payment(gateway, "txn_123456")
```

## Important Notes

1. **API Keys**: Keep consumer key and secret secure
2. **Amounts**: All amounts are in tiyin (1 UZS = 100 tiyin)
3. **Webhook Security**: Always verify webhook signatures
4. **Test Environment**: Use test mode during development
5. **Error Handling**: Wrap all API calls in try-catch blocks

## Complete Configuration for Django and FastAPI

### Django settings.py

```python
# settings.py
PAYTECHUZ = {
    'ATMOS': {
        'CONSUMER_KEY': 'your_atmos_consumer_key',
        'CONSUMER_SECRET': 'your_atmos_consumer_secret',
        'STORE_ID': 'your_atmos_store_id',
        'TERMINAL_ID': 'your_atmos_terminal_id',  # Optional
        'API_KEY': 'your_atmos_api_key',  # For webhook signature verification
        'ACCOUNT_MODEL': 'myapp.models.Order',  # Order model
        'ACCOUNT_FIELD': 'id',  # Order ID field
        'IS_TEST_MODE': True,  # Set to False in production
    }
}
```

### FastAPI environment variables

```python
# .env file
ATMOS_CONSUMER_KEY=your_atmos_consumer_key
ATMOS_CONSUMER_SECRET=your_atmos_consumer_secret
ATMOS_STORE_ID=your_atmos_store_id
ATMOS_TERMINAL_ID=your_atmos_terminal_id
ATMOS_API_KEY=your_atmos_api_key
ATMOS_IS_TEST_MODE=True

# Usage in FastAPI
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

## Additional Information

- [Atmos Official Documentation](https://atmos.uz/developers)
- [PayTechUZ GitHub Repository](https://github.com/PayTechUz/paytechuz)
- [Django Integration](django_integration.md)
- [FastAPI Integration](fastapi_integration.md)
