"""
Forms for the orders app.
"""
from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """
    Form for creating and updating orders.
    """
    class Meta:
        model = Order
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
