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

## API Key Sozlash

PayTechUZ ishlatish uchun API key kerak. API key olish uchun Telegram'da **@muhammadali_me** bilan bog'laning.

API key ni environment variable sifatida sozlang:

```bash
# Linux/macOS
export PAYTECH_API_KEY="sizning-api-key"

# Windows
set PAYTECH_API_KEY=sizning-api-key
```

Yoki FastAPI config.py da:

```python
import os

# API Key
PAYTECH_API_KEY = os.getenv('PAYTECH_API_KEY')
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
import os
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

# Buyurtmani olish
order = db.query(Order).filter(Order.id == 1).first()

# Payme to'lov linkini yaratish
payme = PaymeGateway(
    payme_id='sizning_payme_id',
    payme_key='sizning_payme_key',
    is_test_mode=True,  # Ishlab chiqarish (production) muhitida False qiymatini bering
    api_key=os.getenv('PAYTECH_API_KEY')  # API key
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
    is_test_mode=True,  # Ishlab chiqarish (production) muhitida False qiymatini bering
    api_key=os.getenv('PAYTECH_API_KEY')  # API key
)
click_link = click.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return"
)

# Click karta tokeni bilan to'lov
# 1. Karta tokeni so'rash
card_token_response = click.card_token_request(
    card_number="5614681005030279",
    expire_date="0330",
    temporary=0
)
# Javob: {
#     "error_code": 0,
#     "error_note": "",
#     "card_token": "F64C0AD1-8744-4996-ACCC-E93129F3CB26",
#     "phone_number": "********1717",
#     "temporary": false,
#     "eps_id": "0064"
# }

# 2. Karta tokenini SMS kodi bilan tasdiqlash
verify_response = click.card_token_verify(
    card_token="F64C0AD1-8744-4996-ACCC-E93129F3CB26",
    sms_code=188375
)
# Javob: {
#     "error_code": 0,
#     "error_note": "",
#     "card_number": "561468******0279",
#     "eps_id": "0064"
# }

# 3. Tasdiqlangan karta tokeni bilan to'lov qilish
payment_response = click.card_token_payment(
    card_token="F64C0AD1-8744-4996-ACCC-E93129F3CB26",
    amount=1000,
    transaction_parameter="PAYMENT_1761563561"
)
# Javob: {
#     "error_code": 0,
#     "error_note": "Успешно проведен",
#     "payment_id": "4493670625",
#     "payment_status": 2,
#     "eps_id": "0064"
# }

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

## Click Karta Tokeni Bilan To'lov

Click payment gateway karta tokeni bilan to'lovni quyidagi 3 bosqichda amalga oshirish mumkin:

### 1. Karta Tokeni So'rash

Foydalanuvchining karta ma'lumotlarini Click API ga yuborib, karta tokeni olish:

```python
from fastapi import FastAPI, HTTPException
from paytechuz.gateways.click import ClickGateway

app = FastAPI()

click = ClickGateway(
    service_id='sizning_service_id',
    merchant_id='sizning_merchant_id',
    merchant_user_id='sizning_merchant_user_id',
    secret_key='sizning_secret_key',
    is_test_mode=True
)

@app.post("/click/request-card-token")
async def request_card_token(card_number: str, expire_date: str):
    """
    Karta tokeni so'rash

    Args:
        card_number: Karta raqami (masalan: "5614681005030279")
        expire_date: Karta muddati (masalan: "0330" - 2030-yil mart oyi)
    """
    try:
        response = click.card_token_request(
            card_number=card_number,
            expire_date=expire_date,
            temporary=0
        )

        if response.get('error_code') == 0:
            return {
                "success": True,
                "card_token": response.get('card_token'),
                "phone_number": response.get('phone_number'),
                "message": "Karta tokeni muvaffaqiyatli olindi. SMS kodi yuborildi."
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=response.get('error_note', 'Xato yuz berdi')
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Karta Tokenini Tasdiqlash

Foydalanuvchi SMS kodi orqali karta tokenini tasdiqlash:

```python
@app.post("/click/verify-card-token")
async def verify_card_token(card_token: str, sms_code: int):
    """
    Karta tokenini SMS kodi bilan tasdiqlash

    Args:
        card_token: Oldingi bosqichda olingan karta tokeni
        sms_code: Foydalanuvchiga yuborilgan SMS kodi
    """
    try:
        response = click.card_token_verify(
            card_token=card_token,
            sms_code=sms_code
        )

        if response.get('error_code') == 0:
            return {
                "success": True,
                "card_number": response.get('card_number'),
                "message": "Karta tokeni muvaffaqiyatli tasdiqlandi"
            }
        elif response.get('error_code') == -301:
            raise HTTPException(
                status_code=400,
                detail="SMS kodi muddati tugadi. Qayta so'rash kerak."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=response.get('error_note', 'Xato yuz berdi')
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Tasdiqlangan Karta Tokeni Bilan To'lov

Tasdiqlangan karta tokeni orqali to'lov amalga oshirish:

```python
@app.post("/click/pay-with-card-token")
async def pay_with_card_token(
    card_token: str,
    amount: float,
    transaction_parameter: str
):
    """
    Tasdiqlangan karta tokeni bilan to'lov qilish

    Args:
        card_token: Tasdiqlangan karta tokeni
        amount: To'lov miqdori (som)
        transaction_parameter: Noyob tranzaksiya parametri
    """
    try:
        response = click.card_token_payment(
            card_token=card_token,
            amount=amount,
            transaction_parameter=transaction_parameter
        )

        if response.get('error_code') == 0:
            return {
                "success": True,
                "payment_id": response.get('payment_id'),
                "payment_status": response.get('payment_status'),
                "message": "To'lov muvaffaqiyatli amalga oshirildi"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=response.get('error_note', 'To'lov amalga oshmadi')
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Karta Tokeni To'lov Jarayoni

Karta tokeni bilan to'lovning to'liq jarayoni:

```python
# 1. Foydalanuvchi karta ma'lumotlarini kiritadi
# POST /click/request-card-token
# {
#     "card_number": "5614681005030279",
#     "expire_date": "0330"
# }

# 2. Foydalanuvchi SMS kodi orqali tasdiqlaydi
# POST /click/verify-card-token
# {
#     "card_token": "F64C0AD1-8744-4996-ACCC-E93129F3CB26",
#     "sms_code": 188375
# }

# 3. Tasdiqlangan karta tokeni bilan to'lov amalga oshiriladi
# POST /click/pay-with-card-token
# {
#     "card_token": "F64C0AD1-8744-4996-ACCC-E93129F3CB26",
#     "amount": 1000,
#     "transaction_parameter": "PAYMENT_1761563561"
# }
```

