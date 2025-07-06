from app.models import Order
from paytechuz.integrations.fastapi import PaymeWebhookHandler, ClickWebhookHandler

class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction):
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "paid"
            self.db.commit()

    def cancelled_payment(self, params, transaction):
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "cancelled"
            self.db.commit()

class CustomClickWebhookHandler(ClickWebhookHandler):
    def successfully_payment(self, params, transaction):
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "paid"
            self.db.commit()

    def cancelled_payment(self, params, transaction):
        order = self.db.query(Order).filter(Order.id == transaction.account_id).first()
        if order:
            order.status = "cancelled"
            self.db.commit()
