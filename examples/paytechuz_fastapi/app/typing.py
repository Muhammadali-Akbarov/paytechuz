from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderCreate(BaseModel):
    """Request model for creating an order"""
    product_name: str
    amount: float
    description: Optional[str] = None
    payment_method: str


class OrderResponse(BaseModel):
    """Response model for order data"""
    id: int
    product_name: str
    amount: float
    status: str
    created_at: datetime
    payment_method: str
    payment_link: str

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Response model for invoice data"""
    id: int
    order_id: int
    amount: float
    status: str
    payment_method: str
    payment_link: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """Simplified response model for payment data"""
    id: int
    amount: float
    payment_method: str
    payment_link: Optional[str] = None


class PaymentLinkRequest(BaseModel):
    """Request model for generating payment link"""
    order_id: int
    payment_method: str  # "payme", "click" or "atmos"
    return_url: Optional[str] = "https://example.com/return"


class PaymentLinkResponse(BaseModel):
    """Response model for payment link"""
    order_id: int
    payment_method: str
    payment_link: str


class OrderUpdate(BaseModel):
    """Request model for updating an order"""
    product_name: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None


class OrderListResponse(BaseModel):
    """Response model for order list"""
    orders: list[OrderResponse]
    total: int
    skip: int
    limit: int


class ErrorResponse(BaseModel):
    """Response model for error messages"""
    detail: str
    error_code: Optional[str] = None
