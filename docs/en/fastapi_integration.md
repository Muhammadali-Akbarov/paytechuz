# PayTechUZ FastAPI Integration

## Overview

PayTechUZ is a unified payment library for integration with popular payment systems in Uzbekistan (Payme and Click). This document demonstrates how to integrate the Payme payment system with FastAPI.

## Installation

```bash
pip install paytechuz[fastapi]
```

### 1. Create a Custom Webhook Handler

Create a custom webhook handler by extending the `PaymeWebhookHandler` class:

```python
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.db import get_db
from app.models.models import Order
from paytechuz.integrations.fastapi import PaymeWebhookHandler

# Payme configuration
PAYME_ID = 'your_payme_id'
PAYME_KEY = 'your_payme_key'

class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    """
    Custom Payme webhook handler.
    """
    def successfully_payment(self, params: Dict[str, Any], transaction) -> None:
        """
        Called when payment is successful.
        """
        # Update order status
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "paid"
            self.db.commit()

    def cancelled_payment(self, params: Dict[str, Any], transaction) -> None:
        """
        Called when payment is cancelled.
        """
        # Update order status
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "cancelled"
            self.db.commit()
```

### 2. Create a Webhook Endpoint

Create an endpoint to handle Payme webhook requests:

```python
router = APIRouter()

@router.post("/payments/payme/webhook")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Payme webhook requests.
    """
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

## Webhook Handler Methods

The `PaymeWebhookHandler` class provides several methods that you can override to customize the behavior:

### `successfully_payment(params, transaction)`

Called when a payment is successfully completed. Use this method to update your order status or perform other actions.

### `cancelled_payment(params, transaction)`

Called when a payment is cancelled. Use this method to update your order status or perform other actions.

### Other Available Methods

- `transaction_created(params, transaction, account)`: Called when a transaction is created
- `transaction_already_exists(params, transaction)`: Called when a transaction already exists
- `check_transaction(params, transaction)`: Called when checking a transaction
- `before_check_perform_transaction(params, account)`: Called before checking if a transaction can be performed

## Supported Payme API Methods

The webhook handler supports the following Payme API methods:

1. `CheckPerformTransaction`: Checks if a transaction can be performed
2. `CreateTransaction`: Creates a new transaction
3. `PerformTransaction`: Performs a transaction (marks it as paid)
4. `CheckTransaction`: Checks the status of a transaction
5. `CancelTransaction`: Cancels a transaction
6. `GetStatement`: Gets a list of transactions

## Transaction States

The `PaymentTransaction` model has the following states:

- `CREATED = 0`: Transaction is created
- `INITIATING = 1`: Transaction is being initiated
- `SUCCESSFULLY = 2`: Transaction is successfully completed
- `CANCELLED = -2`: Transaction is cancelled after being successfully performed
- `CANCELLED_DURING_INIT = -1`: Transaction is cancelled during initiation

## Cancellation Reasons

When a transaction is cancelled, a reason code is stored in the `reason` field of the transaction. This reason code is provided by the Payme API and can be used to determine why the transaction was cancelled.

## Database Integration

PayTechUZ automatically creates and manages the necessary database tables for storing payment transactions. The `PaymentTransaction` model includes the following fields:

- `id`: Primary key
- `gateway`: Payment gateway (payme or click)
- `transaction_id`: Transaction ID from the payment system
- `account_id`: Account or order ID
- `amount`: Payment amount
- `state`: Transaction state
- `reason`: Reason for cancellation (if applicable)
- `extra_data`: Additional data for the transaction
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `performed_at`: Payment timestamp
- `cancelled_at`: Cancellation timestamp

## Error Handling

The webhook handler automatically handles errors and returns appropriate responses according to the Payme API specification. All errors are returned with a 200 status code, as required by the Payme API.

## Security

The webhook handler verifies the authentication credentials provided by Payme in the request headers. Make sure to keep your `payme_key` secure and never expose it in client-side code.

## Best Practices

1. Always override the `successfully_payment` and `cancelled_payment` methods to update your order status
2. Use the `one_time_payment` parameter to control whether multiple payments are allowed for the same account
3. Store additional data in the `extra_data` field if needed
4. Use the `reason` field to determine why a transaction was cancelled

## Example Implementation

See the example implementation in the code snippet above for a complete working example.
