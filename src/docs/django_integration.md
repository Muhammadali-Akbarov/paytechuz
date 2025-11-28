# PayTechUZ Django Integratsiyasi

PayTechUZ kutubxonasi Django bilan to'liq integratsiyani ta'minlaydi va Payme, Click, va Atmos to'lov tizimlarini qo'llab-quvvatlaydi.

## O'rnatish

1. Kutubxonani Django qo'llab-quvvatlash bilan o'rnating:

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

Yoki Django settings.py da:

```python
import os

# API Key
PAYTECH_API_KEY = os.environ.get('PAYTECH_API_KEY')
```

## Sozlamalar konfiguratsiyasi

`settings.py` faylingizga PAYTECHUZ sozlamalarini qo'shing. Barcha to'lov tizimlari uchun yagona konfiguratsiya formatidan foydalaning:

```python
# settings.py
PAYTECHUZ = {
    'PAYME': {
        'PAYME_ID': 'your_payme_merchant_id',
        'PAYME_KEY': 'your_payme_merchant_key',
        'ACCOUNT_MODEL': 'your_app.models.Order',  # Masalan: 'shop.models.Order'
        'ACCOUNT_FIELD': 'id',
        'AMOUNT_FIELD': 'amount',
        'ONE_TIME_PAYMENT': True,
        'IS_TEST_MODE': True,  # Production muhitida False qiling
    },
    'CLICK': {
        'SERVICE_ID': 'your_click_service_id',
        'MERCHANT_ID': 'your_click_merchant_id',
        'MERCHANT_USER_ID': 'your_click_merchant_user_id',
        'SECRET_KEY': 'your_click_secret_key',
        'ACCOUNT_MODEL': 'your_app.models.Order',
        'COMMISSION_PERCENT': 0.0,
        'IS_TEST_MODE': True,  # Production muhitida False qiling
    },
    'ATMOS': {
        'CONSUMER_KEY': 'your_atmos_consumer_key',
        'CONSUMER_SECRET': 'your_atmos_consumer_secret',
        'STORE_ID': 'your_atmos_store_id',
        'TERMINAL_ID': 'your_atmos_terminal_id',  # Ixtiyoriy
        'API_KEY': 'your_atmos_api_key',  # Webhook imzo tekshirish uchun
        'ACCOUNT_MODEL': 'your_app.models.Order',
        'ACCOUNT_FIELD': 'id',
        'IS_TEST_MODE': True,  # Production muhitida False qiling
    }
}
```

## URL'larni sozlash

Webhook URL'larini loyihangizning asosiy `urls.py` fayliga qo'shing:

```python
# urls.py
from django.urls import path
from .views import PaymeWebhookView, ClickWebhookView, AtmosWebhookView

urlpatterns = [
    # ...
    # PayTechUZ webhook URL'lari
    path('webhooks/payme/', PaymeWebhookView.as_view(), name='payme_webhook'),
    path('webhooks/click/', ClickWebhookView.as_view(), name='click_webhook'),
    path('webhooks/atmos/', AtmosWebhookView.as_view(), name='atmos_webhook'),
]
```

## Webhook View'larini yaratish

Har bir to'lov tizimi uchun maxsus webhook view'larini yarating:

```python
# views.py
from paytechuz.integrations.django.views import (
    BasePaymeWebhookView,
    BaseClickWebhookView,
    BaseAtmosWebhookView
)
from .models import Order
import logging

logger = logging.getLogger(__name__)

class PaymeWebhookView(BasePaymeWebhookView):
    """Payme webhook uchun maxsus view"""

    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
            logger.info(f"Payme: Buyurtma #{order.id} muvaffaqiyatli to'landi")
        except Order.DoesNotExist:
            logger.error(f"Payme: Buyurtma topilmadi: {transaction.account_id}")

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'cancelled'
            order.save()
            logger.info(f"Payme: Buyurtma #{order.id} bekor qilindi")
        except Order.DoesNotExist:
            logger.error(f"Payme: Buyurtma topilmadi: {transaction.account_id}")

class ClickWebhookView(BaseClickWebhookView):
    """Click webhook uchun maxsus view"""

    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
            logger.info(f"Click: Buyurtma #{order.id} muvaffaqiyatli to'landi")
        except Order.DoesNotExist:
            logger.error(f"Click: Buyurtma topilmadi: {transaction.account_id}")

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'cancelled'
            order.save()
            logger.info(f"Click: Buyurtma #{order.id} bekor qilindi")
        except Order.DoesNotExist:
            logger.error(f"Click: Buyurtma topilmadi: {transaction.account_id}")

class AtmosWebhookView(BaseAtmosWebhookView):
    """Atmos webhook uchun maxsus view"""

    def successfully_payment(self, params, transaction):
        """To'lov muvaffaqiyatli bo'lganda chaqiriladi"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'paid'
            order.save()
            logger.info(f"Atmos: Buyurtma #{order.id} muvaffaqiyatli to'landi")
        except Order.DoesNotExist:
            logger.error(f"Atmos: Buyurtma topilmadi: {transaction.account_id}")

    def cancelled_payment(self, params, transaction):
        """To'lov bekor qilinganda chaqiriladi"""
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.status = 'cancelled'
            order.save()
            logger.info(f"Atmos: Buyurtma #{order.id} bekor qilindi")
        except Order.DoesNotExist:
            logger.error(f"Atmos: Buyurtma topilmadi: {transaction.account_id}")
```

## To'lov uchun link yaratish

Django view'ida to'lov linkini yaratish misoli:

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.atmos import AtmosGateway
from .models import Order

def create_payment_link(request, order_id):
    """Buyurtma uchun to'lov linkini yaratish"""
    order = get_object_or_404(Order, id=order_id)
    payment_method = request.GET.get('method', 'payme')  # payme, click, atmos

    try:
        if payment_method == 'payme':
            # Payme to'lov linkini yaratish
            payme_config = settings.PAYTECHUZ['PAYME']
            payme = PaymeGateway(
                payme_id=payme_config['PAYME_ID'],
                payme_key=payme_config['PAYME_KEY'],
                is_test_mode=payme_config.get('IS_TEST_MODE', True),
                api_key=settings.PAYTECH_API_KEY  # API key
            )
            payment_link = payme.create_payment(
                id=order.id,
                amount=int(order.amount * 100),  # Payme tiyin hisobida ishlaydi
                return_url=request.build_absolute_uri('/payment/success/')
            )

        elif payment_method == 'click':
            # Click to'lov linkini yaratish
            click_config = settings.PAYTECHUZ['CLICK']
            click = ClickGateway(
                service_id=click_config['SERVICE_ID'],
                merchant_id=click_config['MERCHANT_ID'],
                merchant_user_id=click_config['MERCHANT_USER_ID'],
                secret_key=click_config['SECRET_KEY'],
                is_test_mode=click_config.get('IS_TEST_MODE', True),
                api_key=settings.PAYTECH_API_KEY  # API key
            )
            payment_link = click.create_payment(
                id=order.id,
                amount=order.amount,
                return_url=request.build_absolute_uri('/payment/success/'),
                description=f"Buyurtma #{order.id} uchun to'lov"
            )

        elif payment_method == 'atmos':
            # Atmos to'lov linkini yaratish
            atmos_config = settings.PAYTECHUZ['ATMOS']
            atmos = AtmosGateway(
                consumer_key=atmos_config['CONSUMER_KEY'],
                consumer_secret=atmos_config['CONSUMER_SECRET'],
                store_id=atmos_config['STORE_ID'],
                terminal_id=atmos_config.get('TERMINAL_ID'),
                is_test_mode=atmos_config.get('IS_TEST_MODE', True),
                api_key=settings.PAYTECH_API_KEY  # API key
            )
            atmos_payment = atmos.create_payment(
                account_id=order.id,
                amount=int(order.amount * 100)  # Atmos tiyin hisobida ishlaydi
            )
            payment_link = atmos_payment['payment_url']

        else:
            return JsonResponse({'error': 'Noto\'g\'ri to\'lov usuli'}, status=400)

        return JsonResponse({
            'success': True,
            'payment_url': payment_link,
            'order_id': order.id,
            'amount': order.amount,
            'method': payment_method
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def payment_success(request):
    """To'lov muvaffaqiyatli yakunlanganda"""
    return render(request, 'payment/success.html')
```
## Webhook URL'larini sozlash

To'lov tizimlarining admin panellarida webhook URL'larini quyidagicha sozlang:

### Payme
```
https://yourdomain.com/webhooks/payme/
```

### Click
```
https://yourdomain.com/webhooks/click/
```

### Atmos
```
https://yourdomain.com/webhooks/atmos/
```

## Click Karta Tokeni Bilan To'lov

Click payment gateway karta tokeni bilan to'lovni quyidagi 3 bosqichda amalga oshirish mumkin:

### 1. Karta Tokeni So'rash

```python
from paytechuz.gateways.click import ClickGateway
from django.conf import settings

click = ClickGateway(
    service_id='sizning_service_id',
    merchant_id='sizning_merchant_id',
    merchant_user_id='sizning_merchant_user_id',
    secret_key='sizning_secret_key',
    is_test_mode=True,
    api_key=settings.PAYTECH_API_KEY  # API key
)

# Karta tokeni so'rash
response = click.card_token_request(
    card_number="5614681005030279",
    expire_date="0330",
    temporary=0
)

if response.get('error_code') == 0:
    card_token = response.get('card_token')
    phone_number = response.get('phone_number')
    # SMS kodi foydalanuvchiga yuborildi
else:
    error_message = response.get('error_note')
```

### 2. Karta Tokenini Tasdiqlash

```python
# Karta tokenini SMS kodi bilan tasdiqlash
response = click.card_token_verify(
    card_token="F64C0AD1-8744-4996-ACCC-E93129F3CB26",
    sms_code=188375
)

if response.get('error_code') == 0:
    card_number = response.get('card_number')
    # Karta tokeni muvaffaqiyatli tasdiqlandi
elif response.get('error_code') == -301:
    # SMS kodi muddati tugadi
    pass
else:
    error_message = response.get('error_note')
```

### 3. Tasdiqlangan Karta Tokeni Bilan To'lov

```python
# Tasdiqlangan karta tokeni bilan to'lov qilish
response = click.card_token_payment(
    card_token="F64C0AD1-8744-4996-ACCC-E93129F3CB26",
    amount=1000,
    transaction_parameter="PAYMENT_1761563561"
)

if response.get('error_code') == 0:
    payment_id = response.get('payment_id')
    payment_status = response.get('payment_status')
    # To'lov muvaffaqiyatli amalga oshirildi
else:
    error_message = response.get('error_note')
```

## Qo'shimcha ma'lumot

- [Atmos integratsiyasi bo'yicha batafsil qo'llanma](atmos_integration.md)
- [FastAPI integratsiyasi](fastapi_integration.md)
- [PayTechUZ GitHub repository](https://github.com/PayTechUz/paytechuz)
