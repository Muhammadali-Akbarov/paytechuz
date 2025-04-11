"""
URL configuration for the orders app.
"""
from django.urls import path
from .views import (
    OrderListView,
    OrderCreateView,
    OrderDetailView,
    OrderPaymentView,
    PaymentCallbackView
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:order_id>/pay/<str:gateway_type>/', OrderPaymentView.as_view(), name='order_payment'),
    path('<int:order_id>/callback/', PaymentCallbackView.as_view(), name='payment_callback'),
]
