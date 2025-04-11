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
    result = await handler.handle_webhook(request)
    return result
```
