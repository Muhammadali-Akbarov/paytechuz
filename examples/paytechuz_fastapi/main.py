from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import init_db, Order
from app.webhook_handlers import CustomPaymeWebhookHandler, CustomClickWebhookHandler
from app.typing import (
    OrderCreate, 
    OrderResponse
)

from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.atmos import AtmosGateway
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler

app = FastAPI()

init_db(engine)

payme = PaymeGateway(
    payme_id="your_payme_id",
    payme_key="your_payme_key",
    is_test_mode=True  # Set to False in production environment
)

click = ClickGateway(
    service_id="your_service_id",
    merchant_id="your_merchant_id",
    merchant_user_id="your_merchant_user_id",
    secret_key="your_secret_key",
    is_test_mode=True  # Set to False in production environment
)

atmos = AtmosGateway(
    consumer_key="your_atmos_consumer_key",
    consumer_secret="your_atmos_consumer_secret",
    store_id="your_atmos_store_id",
    terminal_id="your_atmos_terminal_id",  # Optional
    is_test_mode=True  # Set to False in production environment
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/orders/", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order with payment link"""
    if order_data.payment_method.lower() not in ["payme", "click", "atmos"]:
        raise HTTPException(status_code=400, detail="Invalid payment method. Use 'payme', 'click', or 'atmos'")
    
    db_order = Order(
        product_name=order_data.product_name,
        amount=order_data.amount,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    if order_data.payment_method.lower() == "payme":
        payment_link = payme.create_payment(
            id=str(db_order.id),
            amount=int(db_order.amount * 100),  # Convert to smallest currency unit
            return_url=order_data.return_url
        )
    elif order_data.payment_method.lower() == "click":
        payment_link = click.create_payment(
            id=str(db_order.id),
            amount=int(db_order.amount * 100),  # Convert to smallest currency unit
            description=db_order.product_name,
            return_url=order_data.return_url
        )
    else:  # atmos
        payment_result = atmos.create_payment(
            account_id=str(db_order.id),
            amount=int(db_order.amount * 100)  # Convert to smallest currency unit
        )
        payment_link = payment_result.get("payment_url")
    
    return OrderResponse(
        id=db_order.id,
        product_name=db_order.product_name,
        amount=db_order.amount,
        status=db_order.status,
        created_at=db_order.created_at,
        payment_method=order_data.payment_method.lower(),
        payment_link=payment_link
    )


@app.post("/payments/payme/webhook")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomPaymeWebhookHandler(
        db=db,
        payme_id="your_payme_id",
        payme_key="your_payme_key",
        account_model=Order,
        account_field='id',
        amount_field='amount'
    )
    return await handler.handle_webhook(request)


@app.post("/payments/click/webhook")
async def click_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomClickWebhookHandler(
        db=db,
        service_id="your_service_id",
        secret_key="your_secret_key",
        account_model=Order
    )
    return await handler.handle_webhook(request)


@app.post("/payments/atmos/webhook")
async def atmos_webhook(request: Request, db: Session = Depends(get_db)):
    import json

    # Atmos webhook handler
    atmos_handler = AtmosWebhookHandler(api_key="your_atmos_api_key")

    try:
        # Get request body
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))

        # Process webhook
        response = atmos_handler.handle_webhook(webhook_data)

        if response['status'] == 1:
            # Payment successful
            invoice = webhook_data.get('invoice')

            # Update order status
            order = db.query(Order).filter(Order.id == invoice).first()
            if order:
                order.status = "paid"
                db.commit()

        return response

    except Exception as e:
        return {
            'status': 0,
            'message': f'Error: {str(e)}'
        }
