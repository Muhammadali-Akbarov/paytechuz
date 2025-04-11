"""
Models for the orders app.
"""
from django.db import models


class Order(models.Model):
    """
    Order model.
    """
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (CANCELLED, 'Cancelled'),
    ]
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.amount} som"
    
    def mark_as_paid(self):
        """
        Mark the order as paid.
        """
        self.status = self.PAID
        self.save()
    
    def mark_as_cancelled(self):
        """
        Mark the order as cancelled.
        """
        self.status = self.CANCELLED
        self.save()
