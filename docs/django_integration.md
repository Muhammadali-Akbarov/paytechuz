# Django integratsiyasi

PayTechUZ kutubxonasini Django loyihangizga o'rnatish va sozlash bo'yicha qo'llanma.

## O'rnatish

```bash
pip install paytechuz[django]
```

## Sozlash

### 1. settings.py faylingizga quyidagi sozlamalarni qo'shing:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]

# Payme sozlamalari
PAYME_ID = 'your_payme_merchant_id'
PAYME_KEY = 'your_payme_merchant_key'
PAYME_ACCOUNT_MODEL = 'your_app.YourModel'  # Masalan: 'orders.Order'
PAYME_ACCOUNT_FIELD = 'id'  # Hisob identifikatori uchun maydon
PAYME_AMOUNT_FIELD = 'amount'  # To'lov miqdorini saqlash maydoni
PAYME_ONE_TIME_PAYMENT = True  # Har bir hisob uchun faqat bir marta to'lov qilish

# Click sozlamalari
CLICK_SERVICE_ID = 'your_click_service_id'
CLICK_MERCHANT_ID = 'your_click_merchant_id'
CLICK_SECRET_KEY = 'your_click_secret_key'
CLICK_ACCOUNT_MODEL = 'your_app.YourModel'  # Masalan: 'orders.Order'
CLICK_COMMISSION_PERCENT = 0.0  # Click komissiyasi foizi
```

### 2. URL'larni sozlash

PayTechUZ kutubxonasi endi URL'larni o'z ichiga olmaydi. Siz o'zingizning URL'laringizni yaratishingiz kerak:

```python
# your_app/urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from paytechuz.integrations.django.views import PaymeWebhookView, ClickWebhookView

urlpatterns = [
    # ...
    path('payments/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
```

### 3. To'lov jarayonini sozlash

To'lov jarayonini sozlash uchun, siz o'z modelingizni yaratishingiz va uni PayTechUZ bilan bog'lashingiz kerak:

```python
# your_app/models.py

from django.db import models

class Order(models.Model):
    # Sizning maydonlaringiz
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.amount}"
```

### 4. To'lov hodisalarini boshqarish

To'lov hodisalarini boshqarish uchun, siz o'z webhook view'laringizni yaratishingiz mumkin:

```python
# your_app/views.py

from paytechuz.integrations.django.views import PaymeWebhookView as BasePaymeWebhookView
from paytechuz.integrations.django.views import ClickWebhookView as BaseClickWebhookView
from .models import Order

class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        # Buyurtma holatini yangilash
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.payment_id = transaction.transaction_id
        order.save()

        # Qo'shimcha logika (masalan, email yuborish)
        # self.send_payment_confirmation_email(order)

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        # Buyurtma holatini yangilash
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'payment_cancelled'
        order.save()

        # Qo'shimcha logika
        # self.notify_admin_about_cancelled_payment(order)

class ClickWebhookView(BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        # Buyurtma holatini yangilash
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.payment_id = transaction.transaction_id
        order.save()

        # Qo'shimcha logika (masalan, email yuborish)
        # self.send_payment_confirmation_email(order)

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        # Buyurtma holatini yangilash
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'payment_cancelled'
        order.save()

        # Qo'shimcha logika
        # self.notify_admin_about_cancelled_payment(order)
```
