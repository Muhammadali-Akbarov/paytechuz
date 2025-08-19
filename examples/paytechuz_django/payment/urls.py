# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from payment.views import PaymeWebhookView, ClickWebhookView, AtmosWebhookView


urlpatterns = [
    path('payments/payme/webhook/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/click/webhook/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
    path('payments/atmos/webhook/', csrf_exempt(AtmosWebhookView.as_view()), name='atmos_webhook'),
]
