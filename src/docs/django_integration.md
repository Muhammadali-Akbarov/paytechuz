# PayTechUZ Django Integratsiyasi

## O'rnatish

1. Kutubxonani o'rnating:

```bash
pip install paytechuz[django]
```

2. Django loyihangizning `settings.py` fayliga PayTechUZ ilovasini qo'shing:

```python
INSTALLED_APPS = [
    # ...
    'paytechuz.integrations.django',
]
```

3. Migratsiyalarni yurgazing:

```bash
python manage.py migrate
```

## Order modelini yaratish

Buyurtmalar uchun model yarating:

```python
# models.py
from django.db import models
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('paid', 'To\'langan'),
        ('cancelled', 'Bekor qilingan'),
        ('delivered', 'Yetkazib berilgan'),
    )

    product_name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narxi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return f"{self.id} - {self.product_name} ({self.amount})"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
```

Modelni yaratgandan so'ng, migratsiyalarni yarating va qo'llang:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Asosiy sozlamalar

`settings.py` faylingizga quyidagi sozlamalarni qo'shing:

```python
# Payme sozlamalari
PAYME_ID = 'your_payme_merchant_id'
PAYME_KEY = 'your_payme_merchant_key'
PAYME_ACCOUNT_MODEL = 'your_app.Order'  # Masalan: 'orders.Order'
PAYME_ACCOUNT_FIELD = 'id'
PAYME_AMOUNT_FIELD = 'amount'

# Click sozlamalari
CLICK_SERVICE_ID = 'your_click_service_id'
CLICK_MERCHANT_ID = 'your_click_merchant_id'
CLICK_SECRET_KEY = 'your_click_secret_key'
CLICK_ACCOUNT_MODEL = 'your_app.Order'
```

## URL'larni sozlash

```python
# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from paytechuz.integrations.django.views import PaymeWebhookView, ClickWebhookView

urlpatterns = [
    # ...
    path('payments/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
```

## To'lov hodisalarini boshqarish

```python
# views.py
from paytechuz.integrations.django.views import PaymeWebhookView as BasePaymeWebhookView
from paytechuz.integrations.django.views import ClickWebhookView as BaseClickWebhookView
from .models import Order

class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'cancelled'
        order.save()

class ClickWebhookView(BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save()

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        order_id = transaction.account_id
        order = Order.objects.get(id=order_id)
        order.status = 'cancelled'
        order.save()
```

## To'lov uchun link yaratish

```python
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

# Buyurtmani olish
order = Order.objects.get(id=1)

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
# Click.create_payment() to'g'ridan-to'g'ri to'lov linkini qaytaradi
click_link = click.create_payment(
    id=order.id,
    amount=order.amount,
    return_url="https://example.com/return",
    description="Buyurtma uchun to'lov"
)
```
