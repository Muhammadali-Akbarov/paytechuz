from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
from paytechuz.integrations.fastapi.models import run_migrations

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def init_db(engine):
    run_migrations(engine)  # Creates Payme/Click payment tables
    Base.metadata.create_all(bind=engine)
