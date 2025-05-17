# PayTechUZ Hujjatlari

PayTechUZ hujjatlariga xush kelibsiz. PayTechUZ - O'zbekistondagi mashhur to'lov tizimlari (Payme va Click) bilan integratsiya qilish uchun yagona to'lov kutubxonasi.

## Mavjud integratsiyalar

- [Django integratsiyasi](django_integration.md)
- [FastAPI integratsiyasi](fastapi_integration.md)

## Imkoniyatlar

- Payme va Click to'lov tizimlarini qo'llab-quvvatlash
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

## Asosiy foydalanish

1. Kutubxonani o'rnating
2. Sozlamalarni sozlang
3. Webhook obrabotchiklarini yarating
4. URL endpointlarini sozlang
5. To'lov hodisalarini boshqarish uchun obrabotchiklarni amalga oshiring

Batafsil ko'rsatmalar uchun framework-ga xos integratsiya qo'llanmalariga qarang.
