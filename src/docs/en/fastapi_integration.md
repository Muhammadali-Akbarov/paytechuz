# PayTechUZ FastAPI Integration

## Installation

1. Install the library:

```bash
pip install paytechuz[fastapi]
```

2. Set up database models in your FastAPI application:

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from paytechuz.integrations.fastapi import Base as PaymentsBase
from paytechuz.integrations.fastapi.models import run_migrations
from datetime import datetime, timezone

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

    def __repr__(self):
        return f"<Order {self.id}: {self.product_name} - {self.amount}>"

# Create payment tables using the run_migrations helper function
run_migrations(engine)

# Create Order table
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## Configure Routes

Add the webhook handlers to your FastAPI application:

```python
# main.py
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from paytechuz.integrations.fastapi import PaymeWebhookHandler, ClickWebhookHandler

from .database import SessionLocal
from .models import Order  # Import the Order model created above

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create custom webhook handlers
class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'paid'
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'cancelled'
        self.db.commit()

class CustomClickWebhookHandler(ClickWebhookHandler):
    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'paid'
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'cancelled'
        self.db.commit()

# Register webhook endpoints
@app.post("/payments/payme/")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomPaymeWebhookHandler(
        db=db,
        payme_id='your_payme_merchant_id',
        payme_key='your_payme_merchant_key',
        account_model=Order,
        account_field='id',
        amount_field='amount',
        one_time_payment=True
    )
    return await handler.handle_webhook(request)

@app.post("/payments/click/")
async def click_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomClickWebhookHandler(
        db=db,
        service_id='your_click_service_id',
        secret_key='your_click_secret_key',
        account_model=Order
    )
    return await handler.handle_webhook(request)
```

## Create Payment Links

```python
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

# Get the order
order = db.query(Order).filter(Order.id == 1).first()

# Generate Payme payment link
payme = PaymeGateway(
    payme_id='your_payme_id',
    payme_key='your_payme_key',
    is_test_mode=True  # Set to False in production environment
)
payme_link = payme.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return"
)

# Generate Click payment link
click = ClickGateway(
    service_id='your_service_id',
    merchant_id='your_merchant_id',
    merchant_user_id='your_merchant_user_id',
    secret_key='your_secret_key',
    is_test_mode=True  # Set to False in production environment
)
click_link = click.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return"
)

# Generate Atmos payment link
from paytechuz.gateways.atmos import AtmosGateway

atmos = AtmosGateway(
    consumer_key='your_consumer_key',
    consumer_secret='your_consumer_secret',
    store_id='your_store_id',
    terminal_id='your_terminal_id',  # optional
    is_test_mode=True  # Set to False in production environment
)

atmos_payment = atmos.create_payment(
    account_id=order.id,
    amount=order.amount
)
atmos_link = atmos_payment['payment_url']
```

## Atmos FastAPI Webhook Integration

### 1. Create Webhook Endpoint

```python
from fastapi import FastAPI, Request, HTTPException, Depends
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler
from sqlalchemy.orm import Session
import json

app = FastAPI()

# Atmos webhook handler
atmos_webhook = AtmosWebhookHandler(api_key="your_atmos_api_key")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/webhooks/atmos/")
async def atmos_webhook_endpoint(request: Request, db: Session = Depends(get_db)):
    """
    Atmos webhook endpoint
    """
    try:
        # Get request body
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))

        # Process webhook
        response = atmos_webhook.handle_webhook(webhook_data)

        if response['status'] == 1:
            # Payment successful
            transaction_id = webhook_data.get('transaction_id')
            amount = webhook_data.get('amount')
            invoice = webhook_data.get('invoice')

            # Update order status
            order = db.query(Order).filter(Order.id == invoice).first()
            if order:
                order.status = "paid"
                db.commit()

                print(f"Order #{order.id} successfully paid")
            else:
                print(f"Order not found: {invoice}")

        return response

    except Exception as e:
        print(f"Webhook error: {e}")
        return {
            'status': 0,
            'message': f'Error: {str(e)}'
        }

@app.get("/payment/atmos/{order_id}")
async def create_atmos_payment(order_id: int, db: Session = Depends(get_db)):
    """
    Create Atmos payment endpoint
    """
    try:
        # Find order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Create Atmos payment
        atmos = AtmosGateway(
            consumer_key='your_consumer_key',
            consumer_secret='your_consumer_secret',
            store_id='your_store_id',
            is_test_mode=True
        )

        payment = atmos.create_payment(
            account_id=order.id,
            amount=order.amount
        )

        return {
            "payment_url": payment['payment_url'],
            "transaction_id": payment['transaction_id'],
            "order_id": order.id,
            "amount": order.amount
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payment/status/atmos/{transaction_id}")
async def check_atmos_payment_status(transaction_id: str):
    """
    Check Atmos payment status endpoint
    """
    try:
        atmos = AtmosGateway(
            consumer_key='your_consumer_key',
            consumer_secret='your_consumer_secret',
            store_id='your_store_id',
            is_test_mode=True
        )

        status = atmos.check_payment(transaction_id)

        return {
            "transaction_id": transaction_id,
            "status": status['status'],
            "details": status['details']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Handle Payment Events

The webhook handlers provide several methods that you can override to customize the behavior:

```python
class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def transaction_created(self, params, transaction, account):
        """Called when a transaction is created"""
        print(f"Transaction created: {transaction.transaction_id}")

    def transaction_already_exists(self, params, transaction):
        """Called when a transaction already exists"""
        print(f"Transaction already exists: {transaction.transaction_id}")

    def successfully_payment(self, params, transaction):
        """Called when payment is successful"""
        print(f"Payment successful: {transaction.transaction_id}")
        # Update your order status
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = 'paid'
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        """Called when payment is cancelled"""
        print(f"Payment cancelled: {transaction.transaction_id}")
        # Update your order status
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        order.status = 'cancelled'
        self.db.commit()
```

The same methods are available for the `ClickWebhookHandler` class.
