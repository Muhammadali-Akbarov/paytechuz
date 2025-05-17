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
        merchant_id='your_click_merchant_id',
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
```


