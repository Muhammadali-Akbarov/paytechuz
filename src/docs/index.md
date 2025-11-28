# PayTechUZ Hujjatlari

PayTechUZ hujjatlariga xush kelibsiz. PayTechUZ - O'zbekistondagi mashhur to'lov tizimlari (Payme, Click va Atmos) bilan integratsiya qilish uchun yagona to'lov kutubxonasi.

## Mavjud integratsiyalar

- [Django integratsiyasi](django_integration.md)
- [FastAPI integratsiyasi](fastapi_integration.md)
- [Atmos integratsiyasi](atmos_integration.md)

## Imkoniyatlar

- Payme, Click va Atmos to'lov tizimlarini qo'llab-quvvatlash
- Django va FastAPI bilan oson integratsiya
- Moslashtirilgan webhook obrabotchiklari
- Avtomatik tranzaksiyalarni boshqarish
- Xavfsiz autentifikatsiya

## O'rnatish

PayTechUZ kutubxonasini barcha bog'liqliklar bilan o'rnatish:

```bash
pip install paytechuz
```

Maxsus framework uchun qo'llab-quvvatlash:

```bash
# Django uchun
pip install paytechuz[django]

# FastAPI uchun
pip install paytechuz[fastapi]
```

## API Key Sozlash

**⚠️ Muhim**: PayTechUZ ishlatish uchun API key talab qilinadi.

### API Key Olish

API key olish uchun Telegram'da **@muhammadali_me** bilan bog'laning.

### Sozlash Usullari

#### 1-usul: Environment Variable (Tavsiya etiladi)

```bash
# Linux/macOS
export PAYTECH_API_KEY="sizning-api-key"

# Windows
set PAYTECH_API_KEY=sizning-api-key

# .env faylida
PAYTECH_API_KEY=sizning-api-key
```

#### 2-usul: Kodda To'g'ridan-to'g'ri

```python
from paytechuz.gateways.payme import PaymeGateway

gateway = PaymeGateway(
    payme_id="...",
    payme_key="...",
    api_key="sizning-api-key"  # API key ni to'g'ridan-to'g'ri bering
)
```

### Xatoliklarni Hal Qilish

**Xato**: "Missing api_key for paytechuz"
- **Yechim**: `PAYTECH_API_KEY` environment variable ni sozlang yoki `api_key` parametrini bering

**Xato**: "Invalid api_key for paytechuz"
- **Yechim**: API key to'g'riligini tekshiring. Agar muammo davom etsa, @muhammadali_me bilan bog'laning

Batafsil ma'lumot uchun: [API_KEY_SETUP.md](../API_KEY_SETUP.md)

## Asosiy foydalanish

1. Kutubxonani o'rnating
2. Sozlamalarni sozlang
3. Webhook obrabotchiklarini yarating
4. URL endpointlarini sozlang
5. To'lov hodisalarini boshqarish uchun obrabotchiklarni amalga oshiring

Batafsil ko'rsatmalar uchun framework-ga xos integratsiya qo'llanmalariga qarang.
