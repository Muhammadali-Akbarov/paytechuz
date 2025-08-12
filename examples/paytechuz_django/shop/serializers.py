from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    
    class Meta:
        model = Order
        fields = ['id', 'product_name', 'amount', 'status', 'payment_type', 'payment_url', 'created_at']
        read_only_fields = ['id', 'status', 'payment_url', 'created_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""
    
    class Meta:
        model = Order
        fields = ['product_name', 'amount', 'payment_type']
        
    def validate_amount(self, value):
        """Validate that amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
        
    def validate_payment_type(self, value):
        """Validate payment type."""
        if value not in ['payme', 'click']:
            raise serializers.ValidationError("Payment type must be either 'payme' or 'click'")
        return value


class PaymentLinkResponseSerializer(serializers.Serializer):
    """Serializer for payment link response."""
    order_id = serializers.IntegerField()
    payment_url = serializers.URLField()
    payment_type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField()
