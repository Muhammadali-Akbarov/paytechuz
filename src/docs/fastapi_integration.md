# PayTechUZ FastAPI Integratsiyasi

## O'rnatish

1. Kutubxonani o'rnating:

```bash
pip install paytechuz[fastapi]
```

2. FastAPI ilovangizda ma'lumotlar bazasi modellarini sozlang:

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from paytechuz.integrations.fastapi import Base as PaymentsBase
from paytechuz.integrations.fastapi.models import run_migrations
from datetime import datetime, timezone

# Ma'lumotlar bazasi uchun engine yaratish
SQLALCHEMY_DATABASE_URL = "sqlite:///./payments.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Asosiy Base yaratish
Base = declarative_base()

# Order modelini yaratish
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Order {self.id}: {self.product_name} - {self.amount}>"

# To'lov jadvallarini run_migrations yordamchi funksiyasi bilan yaratish
run_migrations(engine)

# Order jadvalini yaratish
Base.metadata.create_all(bind=engine)

# Sessiya yaratish
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## URL'larni sozlash

FastAPI ilovangizga webhook obrabotchiklar qo'shing:

```python
# main.py
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from paytechuz.integrations.fastapi import PaymeWebhookHandler, ClickWebhookHandler

from .database import SessionLocal
from .models import Order  # Yuqorida yaratilgan Order modelini import qilish

app = FastAPI()

# Ma'lumotlar bazasi sessiyasini olish uchun dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Maxsus webhook obrabotchiklarni yaratish
class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'paid'
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'cancelled'
        self.db.commit()

class CustomClickWebhookHandler(ClickWebhookHandler):
    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'paid'
        self.db.commit()

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        order_id = transaction.account_id
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = 'cancelled'
        self.db.commit()

# Webhook endpointlarini ro'yxatdan o'tkazish
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

## To'lov uchun link yaratish

```python
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

# Buyurtmani olish
order = db.query(Order).filter(Order.id == 1).first()

# Payme to'lov linkini yaratish
payme = PaymeGateway(
    payme_id='sizning_payme_id',
    payme_key='sizning_payme_key',
    is_test_mode=True  # Ishlab chiqarish (production) muhitida False qiymatini bering
)
payme_link = payme.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return"
)

# Click to'lov linkini yaratish
click = ClickGateway(
    service_id='sizning_service_id',
    merchant_id='sizning_merchant_id',
    merchant_user_id='sizning_merchant_user_id',
    secret_key='sizning_secret_key',
    is_test_mode=True  # Ishlab chiqarish (production) muhitida False qiymatini bering
)
click_link = click.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return"
)

# Atmos to'lov linkini yaratish
from paytechuz.gateways.atmos import AtmosGateway

atmos = AtmosGateway(
    consumer_key='sizning_consumer_key',
    consumer_secret='sizning_consumer_secret',
    store_id='sizning_store_id',
    terminal_id='sizning_terminal_id',  # ixtiyoriy
    is_test_mode=True  # Ishlab chiqarish (production) muhitida False qiymatini bering
)

atmos_payment = atmos.create_payment(
    account_id=order.id,
    amount=order.amount
)
atmos_link = atmos_payment['payment_url']
```

## Atmos FastAPI Webhook Integration

### 1. Webhook endpoint yaratish

```python
from fastapi import FastAPI, Request, HTTPException, Depends
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler
from sqlalchemy.orm import Session
import json

app = FastAPI()

# Atmos webhook handler
atmos_webhook = AtmosWebhookHandler(api_key="sizning_atmos_api_key")

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
        # Request body ni olish
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))

        # Webhook ni qayta ishlash
        response = atmos_webhook.handle_webhook(webhook_data)

        if response['status'] == 1:
            # To'lov muvaffaqiyatli
            transaction_id = webhook_data.get('transaction_id')
            amount = webhook_data.get('amount')
            invoice = webhook_data.get('invoice')

            # Buyurtma holatini yangilash
            order = db.query(Order).filter(Order.id == invoice).first()
            if order:
                order.status = "paid"
                db.commit()

                print(f"Buyurtma #{order.id} muvaffaqiyatli to'landi")
            else:
                print(f"Buyurtma topilmadi: {invoice}")

        return response

    except Exception as e:
        print(f"Webhook xatosi: {e}")
        return {
            'status': 0,
            'message': f'Error: {str(e)}'
        }

@app.get("/payment/atmos/{order_id}")
async def create_atmos_payment(order_id: int, db: Session = Depends(get_db)):
    """
    Atmos to'lov yaratish endpoint
    """
    try:
        # Buyurtmani topish
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

        # Atmos to'lov yaratish
        atmos = AtmosGateway(
            consumer_key='sizning_consumer_key',
            consumer_secret='sizning_consumer_secret',
            store_id='sizning_store_id',
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
    Atmos to'lov holatini tekshirish endpoint
    """
    try:
        atmos = AtmosGateway(
            consumer_key='sizning_consumer_key',
            consumer_secret='sizning_consumer_secret',
            store_id='sizning_store_id',
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

### 2. Atmos to'lov jarayoni

```python
# To'lov yaratish va foydalanuvchini yo'naltirish
@app.post("/create-payment/")
async def create_payment(order_data: dict, db: Session = Depends(get_db)):
    """
    Yangi buyurtma yaratish va to'lov linkini qaytarish
    """
    try:
        # Buyurtma yaratish
        order = Order(
            product_name=order_data['product_name'],
            amount=order_data['amount'],
            status="pending"
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        # Atmos to'lov yaratish
        atmos = AtmosGateway(
            consumer_key='sizning_consumer_key',
            consumer_secret='sizning_consumer_secret',
            store_id='sizning_store_id',
            is_test_mode=True
        )

        payment = atmos.create_payment(
            account_id=order.id,
            amount=order.amount
        )

        return {
            "order_id": order.id,
            "payment_url": payment['payment_url'],
            "transaction_id": payment['transaction_id'],
            "message": "To'lov yaratildi. Foydalanuvchini payment_url ga yo'naltiring."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```


