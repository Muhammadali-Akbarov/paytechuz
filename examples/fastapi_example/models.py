"""
Database models for FastAPI example.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import Session

from .database import Base
from . import schemas


class Order(Base):
    """
    Order model.
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get(cls, db: Session, order_id: int) -> Optional["Order"]:
        """
        Get an order by ID.
        """
        return db.query(cls).filter(cls.id == order_id).first()
    
    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100) -> List["Order"]:
        """
        Get all orders.
        """
        return db.query(cls).offset(skip).limit(limit).all()
    
    @classmethod
    def create(cls, db: Session, order: schemas.OrderCreate) -> "Order":
        """
        Create a new order.
        """
        db_order = cls(amount=order.amount)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def mark_as_paid(self, db: Session) -> "Order":
        """
        Mark the order as paid.
        """
        self.status = "paid"
        db.commit()
        db.refresh(self)
        return self
    
    def mark_as_cancelled(self, db: Session) -> "Order":
        """
        Mark the order as cancelled.
        """
        self.status = "cancelled"
        db.commit()
        db.refresh(self)
        return self
