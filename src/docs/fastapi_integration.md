# PayTechUZ FastAPI Integratsiyasi

## Umumiy ma'lumot

PayTechUZ - bu O'zbekistondagi mashhur to'lov tizimlari (Payme va Click) bilan integratsiya qilish uchun yagona to'lov kutubxonasi. Ushbu hujjat FastAPI bilan Payme to'lov tizimini integratsiya qilishni ko'rsatadi.

## O'rnatish

```bash
pip install paytechuz[fastapi]
```

### 1. Maxsus Webhook Handler yaratish
`PaymeWebhookHandler` klassini kengaytirish orqali maxsus webhook handler yarating:

```python
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.db import get_db
from app.models.models import Order
from paytechuz.integrations.fastapi import PaymeWebhookHandler

# Payme konfiguratsiyasi
PAYME_ID = 'sizning_payme_id'
PAYME_KEY = 'sizning_payme_key'

class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    """
    Maxsus Payme webhook handler.
    """
    def successfully_payment(self, params: Dict[str, Any], transaction) -> None:
        """
        To'lov muvaffaqiyatli bo'lganda chaqiriladi.
        """
        # Buyurtma holatini yangilash
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "paid"
            self.db.commit()

    def cancelled_payment(self, params: Dict[str, Any], transaction) -> None:
        """
        To'lov bekor qilinganda chaqiriladi.
        """
        # Buyurtma holatini yangilash
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "cancelled"
            self.db.commit()
```

### 2. Webhook Endpoint yaratish

Payme webhook so'rovlarini qayta ishlash uchun endpoint yarating:

```python
router = APIRouter()

@router.post("/payments/payme/webhook")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Payme webhook so'rovlarini qayta ishlash.
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
    result = await handler.h    andle_webhook(request)
    return result
```

### 3. To'lov uchun link generate qilish

```python
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

@app.get("/generate-payment/{order_id}")
async def generate_payment(order_id: int):
    order = await db.get_order(id=order_id)  # Your database query here
    
    # Click orqali to'lov
    click = ClickGateway()
    click_link = click.generate_payment_link(
        id=order.id,
        amount=order.amount,
        return_url="https://example.com/return",
    )
    
    # Payme orqali to'lov
    payme = PaymeGateway()
    payme_link = payme.generate_payment_link(
        id=order.id,
        amount=order.amount,
        return_url="https://example.com/return",
    )
    
    return {
        "click_payment_url": click_link,
        "payme_payment_url": payme_link
    }

# Async versiyasi
@app.get("/generate-payment-async/{order_id}")
async def generate_payment_async(order_id: int):
    order = await db.get_order(id=order_id)  # Your database query here
    
    # Click orqali to'lov
    click = ClickGateway()
    click_link = await click.generate_payment_link_async(
        id=order.id,
        amount=order.amount,
        return_url="https://example.com/return",
    )
    
    # Payme orqali to'lov
    payme = PaymeGateway()
    payme_link = await payme.generate_payment_link_async(
        id=order.id,
        amount=order.amount,
        return_url="https://example.com/return",
    )
    
    return {
        "click_payment_url": click_link,
        "payme_payment_url": payme_link
    }
```
