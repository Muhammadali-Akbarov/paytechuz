from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrderCreate(BaseModel):
    """Order yaratish uchun request model"""
    product_name: str
    amount: float
    description: Optional[str] = None
    payment_method: str  # "payme", "click" yoki "atmos"
    return_url: Optional[str] = "https://example.com/return"

class OrderResponse(BaseModel):
    """Order ma'lumotlarini qaytarish uchun response model"""
    id: int
    product_name: str
    amount: float
    status: str
    created_at: datetime
    payment_method: str
    payment_link: str

    class Config:
        from_attributes = True

class PaymentLinkRequest(BaseModel):
    """To'lov linkini generatsiya qilish uchun request model"""
    order_id: int
    payment_method: str  # "payme", "click" yoki "atmos"
    return_url: Optional[str] = "https://example.com/return"

class PaymentLinkResponse(BaseModel):
    """To'lov linkini qaytarish uchun response model"""
    order_id: int
    payment_method: str
    payment_link: str

class OrderUpdate(BaseModel):
    """Order yangilash uchun request model"""
    product_name: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None

class OrderListResponse(BaseModel):
    """Orderlar ro'yxatini qaytarish uchun response model"""
    orders: list[OrderResponse]
    total: int
    skip: int
    limit: int

class ErrorResponse(BaseModel):
    """Xatolik xabarini qaytarish uchun response model"""
    detail: str
    error_code: Optional[str] = None 
