from paytechuz.integrations.fastapi import ClickWebhookHandler, PaymeWebhookHandler

from app.models import Invoice


class CustomPaymeWebhookHandler(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction):
        invoice = self.db.query(Invoice).filter(Invoice.id == transaction.account_id).first()
        if invoice:
            invoice.status = "paid"
            self.db.commit()

    def cancelled_payment(self, params, transaction):
        invoice = self.db.query(Invoice).filter(Invoice.id == transaction.account_id).first()
        if invoice:
            invoice.status = "cancelled"
            self.db.commit()


class CustomClickWebhookHandler(ClickWebhookHandler):
    def successfully_payment(self, params, transaction):
        invoice = self.db.query(Invoice).filter(Invoice.id == transaction.account_id).first()
        if invoice:
            invoice.status = "paid"
            self.db.commit()

    def cancelled_payment(self, params, transaction):
        invoice = self.db.query(Invoice).filter(Invoice.id == transaction.account_id).first()
        if invoice:
            invoice.status = "cancelled"
            self.db.commit()
