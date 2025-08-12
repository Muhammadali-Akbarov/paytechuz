from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """Form for creating orders with payment type selection."""
    
    class Meta:
        model = Order
        fields = ['product_name', 'amount', 'payment_type']
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0.01'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_type'].required = True
        self.fields['payment_type'].empty_label = "Select Payment Method"
