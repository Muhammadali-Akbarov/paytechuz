from datetime import datetime, timezone

from sqlalchemy.orm import relationship
from paytechuz.integrations.fastapi.models import run_migrations
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    invoices = relationship("Invoice", back_populates="order")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    payment_method = Column(String, nullable=False)
    payment_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    order = relationship("Order", back_populates="invoices")


def init_db(engine):
    run_migrations(engine)
    Base.metadata.create_all(bind=engine)
