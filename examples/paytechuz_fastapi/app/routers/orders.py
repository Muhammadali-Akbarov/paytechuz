from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_db
from app.gateways import get_gateways
from app.models import Invoice, Order
from app.typing import OrderCreate, PaymentResponse


router = APIRouter(
    prefix="/api/v1",
    tags=["orders"]
)


@router.post("/orders", response_model=PaymentResponse)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order with payment link"""
    payment_method = order_data.payment_method.lower()
    gateway = get_gateways(name=payment_method)

    if not gateway:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method. Use 'payme', 'click', or 'atmos'"
        )

    db_order = Order(
        product_name=order_data.product_name,
        amount=order_data.amount,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    db_invoice = Invoice(
        order_id=db_order.id,
        amount=order_data.amount,
        status="pending",
        payment_method=payment_method
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    payment_link = None

    if payment_method == "payme":
        payment_link = gateway.create_payment(
            id=str(db_invoice.id),
            amount=int(order_data.amount * 100),
            return_url="https://example.com/return"
        )

    if payment_method == "click":
        payment_result = gateway.create_payment(
            id=str(db_invoice.id),
            amount=int(order_data.amount),
            description=db_order.product_name,
            return_url="https://example.com/return"
        )
        payment_link = payment_result.get("payment_url")

    if payment_method == "atmos":
        payment_result = gateway.create_payment(
            account_id=str(db_invoice.id),
            amount=int(order_data.amount * 100)
        )
        payment_link = payment_result.get("payment_url")

    db_invoice.payment_link = payment_link
    db.commit()
    db.refresh(db_invoice)

    return PaymentResponse(
        id=db_order.id,
        amount=order_data.amount,
        payment_method=payment_method,
        payment_link=payment_link
    )
