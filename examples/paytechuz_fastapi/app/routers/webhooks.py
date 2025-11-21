import json

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler

from app import config
from app.models import Invoice
from app.dependencies import get_db
from app.webhook_handlers import CustomClickWebhookHandler, CustomPaymeWebhookHandler


router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["webhooks"]
)


@router.post("/payme")
async def payme_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomPaymeWebhookHandler(
        db=db,
        payme_id=config.PAYME_ID,
        payme_key=config.PAYME_KEY,
        account_model=Invoice,
        account_field='id',
        amount_field='amount'
    )
    return await handler.handle_webhook(request)


@router.post("/click")
async def click_webhook(request: Request, db: Session = Depends(get_db)):
    handler = CustomClickWebhookHandler(
        db=db,
        service_id=config.CLICK_SERVICE_ID,
        secret_key=config.CLICK_SECRET_KEY,
        account_model=Invoice
    )
    return await handler.handle_webhook(request)


@router.post("/atmos")
async def atmos_webhook(request: Request, db: Session = Depends(get_db)):
    atmos_handler = AtmosWebhookHandler(api_key=config.ATMOS_API_KEY)

    try:
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))

        response = atmos_handler.handle_webhook(webhook_data)

        if response['status'] == 1:
            invoice_id = webhook_data.get('invoice')

            invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if invoice:
                invoice.status = "paid"
                db.commit()

        return response

    except Exception as e:
        return {
            'status': 0,
            'message': f'Error: {str(e)}'
        }
