from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(primary_key=True)
    customer_name: Mapped[str]
    customer_email: Mapped[str] = mapped_column(index=True)
    items: Mapped[list[dict]] = mapped_column(JSON)  # [{"name": ..., "qty": ..., "price": ...}]
    total_amount: Mapped[float]
    currency: Mapped[str | None] = mapped_column(default="EUR")
    status: Mapped[str]  # processing | in_transit | delivered
    warehouse: Mapped[str | None] = mapped_column(default="Posti Helsinki Hub")
    order_date: Mapped[datetime]
    delivered_date: Mapped[datetime | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    reason: Mapped[str]
    amount_eur: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(server_default="pending")  # pending | approved | rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
