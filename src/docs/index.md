# PayTechUZ Hujjatlari

PayTechUZ hujjatlariga xush kelibsiz. PayTechUZ - bu O'zbekistondagi mashhur to'lov tizimlari (Payme va Click) bilan integratsiya qilish uchun yagona to'lov kutubxonasi.

## Mavjud integratsiyalar

- [Django integratsiyasi](django_integration.md)
- [FastAPI integratsiyasi](fastapi_integration.md)

## Ingliz tilidagi hujjatlar

- [English Documentation](en/index.md)

## Xususiyatlar

- Payme va Click to'lov tizimlarini qo'llab-quvvatlash
- Django va FastAPI bilan oson integratsiya
- Sozlanuvchi webhook handler'lar
- Avtomatik tranzaksiyalarni boshqarish
- Xavfsiz autentifikatsiya

## O'rnatish

PayTechUZ ni barcha bog'liqliklar bilan o'rnatish uchun:

```bash
pip install paytechuz
```

Maxsus framework qo'llab-quvvatlash uchun:

```bash
# Django uchun
pip install paytechuz[django]

# FastAPI uchun
pip install paytechuz[fastapi]
```

## Asosiy foydalanish

1. Kutubxonani o'rnating
2. Sozlamalarni sozlang
3. Webhook handler'larni yarating
4. URL endpoint'larni sozlang
5. To'lov hodisalarini boshqaruvchilarni amalga oshiring

Batafsil ko'rsatmalar uchun framework-ga xos integratsiya qo'llanmalarini ko'ring.
