"""
Django URLs for PayTechUZ.
"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import PaymeWebhookView, ClickWebhookView

app_name = 'paytechuz'

urlpatterns = [
    path('webhooks/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('webhooks/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
