"""
Flask integration for PayTechUZ.
"""
from .models import db, PaymentTransaction
from .routes import blueprint, PaymeWebhook, ClickWebhook