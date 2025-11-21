from fastapi import FastAPI

from app.database import engine
from app.models import init_db
from app.routers import orders, webhooks

app = FastAPI()

init_db(engine)

app.include_router(orders.router)
app.include_router(webhooks.router)
