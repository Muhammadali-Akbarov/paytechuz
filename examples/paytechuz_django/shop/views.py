from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.atmos import AtmosGateway
from django.conf import settings

from .serializers import OrderCreateSerializer, PaymentLinkResponseSerializer


class CreateOrderAPIView(APIView):
    """API endpoint for creating orders with payment integration."""

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = serializer.save()

        try:
            # Generate payment link based on payment type
            payment_url = generate_payment_link(order)
            order.payment_url = payment_url
            order.save()

            # Return payment link response
            response_data = {
                'order_id': order.id,
                'payment_url': payment_url,
                'payment_type': order.payment_type,
                'amount': order.amount,
                'status': order.status
            }

            response_serializer = PaymentLinkResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            order.delete()  # Clean up the order if payment link creation fails
            return Response(
                {'error': f'Error creating payment link: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


def generate_payment_link(order):
    """Generate payment link based on order's payment type."""
    paytechuz_settings = settings.PAYTECHUZ

    if order.payment_type == 'payme':
        payme = PaymeGateway(
            payme_id=paytechuz_settings['PAYME']['PAYME_ID'],
            payme_key=paytechuz_settings['PAYME']['PAYME_KEY'],
            is_test_mode=paytechuz_settings['PAYME']['IS_TEST_MODE']
        )
        return payme.create_payment(
            id=order.id,
            amount=float(order.amount),
            return_url="https://example.com/return"
        )

    if order.payment_type == 'click':
        click = ClickGateway(
            service_id=paytechuz_settings['CLICK']['SERVICE_ID'],
            merchant_id=paytechuz_settings['CLICK']['MERCHANT_ID'],
            merchant_user_id=paytechuz_settings['CLICK']['MERCHANT_USER_ID'],
            secret_key=paytechuz_settings['CLICK']['SECRET_KEY'],
            is_test_mode=paytechuz_settings['CLICK']['IS_TEST_MODE']
        )
        result = click.create_payment(
            id=order.id,
            amount=float(order.amount),
            return_url="https://example.com/return"
        )
        return result.get("payment_url")

    if order.payment_type == 'atmos':
        atmos = AtmosGateway(
            consumer_key=paytechuz_settings['ATMOS']['CONSUMER_KEY'],
            consumer_secret=paytechuz_settings['ATMOS']['CONSUMER_SECRET'],
            store_id=paytechuz_settings['ATMOS']['STORE_ID'],
            terminal_id=paytechuz_settings['ATMOS'].get('TERMINAL_ID'),
            is_test_mode=paytechuz_settings['ATMOS']['IS_TEST_MODE']
        )
        result = atmos.create_payment(
            account_id=order.id,
            amount=float(order.amount)
        )
        return result.get("payment_url")

    raise ValueError(f"Unsupported payment type: {order.payment_type}")


