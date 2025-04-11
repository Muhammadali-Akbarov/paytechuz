"""
Django admin configuration for PayTechUZ.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentTransaction model.
    """
    list_display = (
        'id',
        'gateway',
        'transaction_id',
        'account_id',
        'amount',
        'state_display',
        'created_at',
        'updated_at',
    )
    list_filter = ('gateway', 'state', 'created_at')
    search_fields = ('transaction_id', 'account_id')
    readonly_fields = (
        'gateway',
        'transaction_id',
        'account_id',
        'amount',
        'state',
        'extra_data',
        'created_at',
        'updated_at',
        'performed_at',
        'cancelled_at',
    )
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'gateway',
                'transaction_id',
                'account_id',
                'amount',
                'state',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'performed_at',
                'cancelled_at',
            )
        }),
        ('Additional Data', {
            'fields': ('extra_data',),
            'classes': ('collapse',),
        }),
    )

    def state_display(self, obj):
        """
        Display the state with a colored badge.
        """
        if obj.state == PaymentTransaction.CREATED:
            return format_html('<span style="background-color: #f8f9fa; color: #212529; padding: 3px 8px; border-radius: 4px;">Created</span>')
        elif obj.state == PaymentTransaction.INITIATING:
            return format_html('<span style="background-color: #fff3cd; color: #856404; padding: 3px 8px; border-radius: 4px;">Initiating</span>')
        elif obj.state == PaymentTransaction.SUCCESSFULLY:
            return format_html('<span style="background-color: #d4edda; color: #155724; padding: 3px 8px; border-radius: 4px;">Successfully</span>')
        elif obj.state == PaymentTransaction.CANCELLED:
            return format_html('<span style="background-color: #f8d7da; color: #721c24; padding: 3px 8px; border-radius: 4px;">Cancelled</span>')
        elif obj.state == PaymentTransaction.CANCELLED_DURING_INIT:
            return format_html('<span style="background-color: #f8d7da; color: #721c24; padding: 3px 8px; border-radius: 4px;">Cancelled (Init)</span>')
        return obj.get_state_display()

    state_display.short_description = 'State'
