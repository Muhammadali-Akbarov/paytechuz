"""
Database models for Flask example.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Order(db.Model):
    """
    Order model.
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Order {self.id} - {self.amount}>"
    
    def mark_as_paid(self):
        """
        Mark the order as paid.
        """
        self.status = 'paid'
        db.session.commit()
    
    def mark_as_cancelled(self):
        """
        Mark the order as cancelled.
        """
        self.status = 'cancelled'
        db.session.commit()
