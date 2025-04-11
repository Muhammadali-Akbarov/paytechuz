"""
Pydantic schemas for FastAPI example.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderBase(BaseModel):
    """
    Base schema for Order.
    """
    amount: float


class OrderCreate(OrderBase):
    """
    Schema for creating an Order.
    """
    pass


class Order(OrderBase):
    """
    Schema for Order.
    """
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
