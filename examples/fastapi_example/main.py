"""
FastAPI example for PayTechUZ.
"""
import os
import sys
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Add parent directory to path to import paytechuz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from paytechuz import create_gateway
from .database import SessionLocal, engine
from . import models, schemas

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PayTechUZ FastAPI Example")

# Templates
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Payment gateway configuration
PAYME_ID = 'your-payme-id'
PAYME_KEY = 'your-payme-key'
CLICK_SERVICE_ID = 'your-service-id'
CLICK_MERCHANT_ID = 'your-merchant-id'
CLICK_SECRET_KEY = 'your-secret-key'


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=RedirectResponse)
def read_root():
    return "/orders"


@app.get("/orders", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = models.Order.get_all(db, skip=skip, limit=limit)
    return orders


@app.post("/orders", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return models.Order.create(db, order)


@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = models.Order.get(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/orders/{order_id}/pay/{gateway_type}")
def pay_order(order_id: int, gateway_type: str, request: Request, db: Session = Depends(get_db)):
    order = models.Order.get(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Create payment gateway
    if gateway_type == 'payme':
        gateway = create_gateway(
            'payme',
            payme_id=PAYME_ID,
            payme_key=PAYME_KEY,
            is_test_mode=True
        )
    elif gateway_type == 'click':
        gateway = create_gateway(
            'click',
            service_id=CLICK_SERVICE_ID,
            merchant_id=CLICK_MERCHANT_ID,
            secret_key=CLICK_SECRET_KEY,
            is_test_mode=True
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid gateway type")
    
    # Create payment
    callback_url = str(request.url_for('payment_callback', order_id=order_id))
    return_url = str(request.url_for('read_order', order_id=order_id))
    
    payment = gateway.create_payment(
        amount=float(order.amount),
        account_id=order.id,
        description=f"Payment for order #{order.id}",
        return_url=return_url,
        callback_url=callback_url
    )
    
    # Redirect to payment URL
    return RedirectResponse(payment['payment_url'])


@app.get("/orders/{order_id}/callback")
def payment_callback(order_id: int, db: Session = Depends(get_db)):
    order = models.Order.get(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # In a real application, you would check the payment status
    # and update the order accordingly
    
    return RedirectResponse(f"/orders/{order_id}")


@app.post("/orders/{order_id}/callback")
def payment_callback_post(order_id: int, db: Session = Depends(get_db)):
    # This would be called by the payment gateway
    # In a real application, you would verify the payment
    # and update the order accordingly
    
    return {"status": "success"}
