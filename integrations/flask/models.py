"""
Flask models for PayTechUZ.
"""
from datetime import datetime
from typing import Dict, Any, Optional

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PaymentTransaction(db.Model):
    """
    Payment transaction model for storing payment information.
    """
    __tablename__ = "paytechuz_transactions"

    # Payment gateway choices
    PAYME = 'payme'
    CLICK = 'click'

    GATEWAY_CHOICES = [
        (PAYME, 'Payme'),
        (CLICK, 'Click'),
    ]

    # Transaction states
    CREATED = 0
    INITIATING = 1
    SUCCESSFULLY = 2
    CANCELLED = -2
    CANCELLED_DURING_INIT = -1

    STATE_CHOICES = [
        (CREATED, "Created"),
        (INITIATING, "Initiating"),
        (SUCCESSFULLY, "Successfully"),
        (CANCELLED, "Cancelled after successful performed"),
        (CANCELLED_DURING_INIT, "Cancelled during initiation"),
    ]

    id = db.Column(db.Integer, primary_key=True)
    gateway = db.Column(db.String(10), index=True)
    transaction_id = db.Column(db.String(255), index=True)
    account_id = db.Column(db.String(255), index=True)
    amount = db.Column(db.Float)
    state = db.Column(db.Integer, default=CREATED, index=True)
    extra_data = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    performed_at = db.Column(db.DateTime, nullable=True, index=True)
    cancelled_at = db.Column(db.DateTime, nullable=True, index=True)

    __table_args__ = (
        db.UniqueConstraint('gateway', 'transaction_id', name='unique_transaction'),
    )

    @classmethod
    def create_transaction(
        cls,
        gateway: str,
        transaction_id: str,
        account_id: str,
        amount: float,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> "PaymentTransaction":
        """
        Create a new transaction or get an existing one.

        Args:
            gateway: Payment gateway (payme or click)
            transaction_id: Transaction ID from the payment system
            account_id: Account or order ID
            amount: Payment amount
            extra_data: Additional data for the transaction

        Returns:
            PaymentTransaction instance
        """
        # Check if transaction already exists
        transaction = cls.query.filter_by(
            gateway=gateway,
            transaction_id=transaction_id
        ).first()

        if transaction:
            return transaction

        # Create new transaction
        transaction = cls(
            gateway=gateway,
            transaction_id=transaction_id,
            account_id=str(account_id),
            amount=amount,
            state=cls.CREATED,
            extra_data=extra_data or {}
        )

        db.session.add(transaction)
        db.session.commit()

        return transaction

    def mark_as_paid(self) -> "PaymentTransaction":
        """
        Mark the transaction as paid.

        Returns:
            PaymentTransaction instance
        """
        if self.state != self.SUCCESSFULLY:
            self.state = self.SUCCESSFULLY
            self.performed_at = datetime.utcnow()
            db.session.commit()

        return self

    def mark_as_cancelled(self, reason: Optional[str] = None) -> "PaymentTransaction":
        """
        Mark the transaction as cancelled.

        Args:
            reason: Reason for cancellation

        Returns:
            PaymentTransaction instance
        """
        if self.state not in [self.CANCELLED, self.CANCELLED_DURING_INIT]:
            # Always set state to CANCELLED (-2) for Payme API compatibility
            # regardless of the current state
            self.state = self.CANCELLED
            self.cancelled_at = datetime.utcnow()

            # Store reason in extra_data if provided
            if reason:
                extra_data = self.extra_data or {}
                extra_data['cancel_reason'] = reason
                self.extra_data = extra_data

            db.session.commit()

        return self
