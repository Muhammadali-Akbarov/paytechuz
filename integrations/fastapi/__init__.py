"""
FastAPI integration for PayTechUZ.
"""
from .models import Base, PaymentTransaction
from .schemas import (
    PaymentTransactionBase,
    PaymentTransactionCreate,
    PaymentTransaction as PaymentTransactionSchema,
    PaymentTransactionList,
    PaymeWebhookRequest,
    PaymeWebhookResponse,
    PaymeWebhookErrorResponse,
    ClickWebhookRequest,
    ClickWebhookResponse
)
from .routes import (
    router,
    PaymeWebhookHandler,
    ClickWebhookHandler
)