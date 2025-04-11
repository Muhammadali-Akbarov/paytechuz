"""
Views for the orders app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.conf import settings
from django.urls import reverse

from paytechuz import create_gateway
from .models import Order
from .forms import OrderForm


class OrderListView(View):
    """
    View to list all orders.
    """
    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')
        return render(request, 'orders/list.html', {'orders': orders})


class OrderCreateView(View):
    """
    View to create a new order.
    """
    def get(self, request):
        form = OrderForm()
        return render(request, 'orders/create.html', {'form': form})
    
    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('order_detail', order_id=order.id)
        return render(request, 'orders/create.html', {'form': form})


class OrderDetailView(View):
    """
    View to display order details.
    """
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/detail.html', {'order': order})


class OrderPaymentView(View):
    """
    View to handle order payment.
    """
    def get(self, request, order_id, gateway_type):
        order = get_object_or_404(Order, id=order_id)
        
        # Create payment gateway
        if gateway_type == 'payme':
            gateway = create_gateway(
                'payme',
                payme_id=settings.PAYME_ID,
                payme_key=settings.PAYME_KEY,
                is_test_mode=True
            )
        elif gateway_type == 'click':
            gateway = create_gateway(
                'click',
                service_id=settings.CLICK_SERVICE_ID,
                merchant_id=settings.CLICK_MERCHANT_ID,
                secret_key=settings.CLICK_SECRET_KEY,
                is_test_mode=True
            )
        else:
            return redirect('order_detail', order_id=order.id)
        
        # Create payment
        callback_url = request.build_absolute_uri(
            reverse('payment_callback', kwargs={'order_id': order.id})
        )
        return_url = request.build_absolute_uri(
            reverse('order_detail', kwargs={'order_id': order.id})
        )
        
        payment = gateway.create_payment(
            amount=float(order.amount),
            account_id=order.id,
            description=f"Payment for order #{order.id}",
            return_url=return_url,
            callback_url=callback_url
        )
        
        # Redirect to payment URL
        return redirect(payment['payment_url'])


class PaymentCallbackView(View):
    """
    View to handle payment callbacks.
    """
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # In a real application, you would check the payment status
        # and update the order accordingly
        
        return redirect('order_detail', order_id=order.id)
    
    def post(self, request, order_id):
        # This would be called by the payment gateway
        # In a real application, you would verify the payment
        # and update the order accordingly
        
        return redirect('order_detail', order_id=order.id)
